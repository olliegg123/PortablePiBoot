import requests
from webexteamsbot import TeamsBot
from webexteamssdk import WebexTeamsAPI
from requests_toolbelt.multipart.encoder import MultipartEncoder
import sys
import time
import pandas as pd
from loguru import logger
import re
import time
import json
import random
import requests
import json
from datetime import datetime, timedelta
import sqlite3
import random
import paho.mqtt.client as mqtt
import urllib.request
import netifaces as ni

time.sleep(20)

##### CORE IMPORTS #######
with open('/home/pi/storage/meraki_details.json') as f:
    merakiDetails = json.load(f)
print(merakiDetails)
with open('/home/pi/storage/keys.json') as f:
    keys = json.load(f)
with open('/home/pi/storage/tailscale.json') as f:
    tailscale_json = json.load(f)

Meraki_API_Key = keys["meraki"]
headers = {
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": Meraki_API_Key
    }
meraki_baseurl = "https://api.meraki.com/api/v1/"


webex_baseurl = 'https://webexapis.com/v1/'
teams_token = keys["webex"]
webexHeaders = {
        "content-type": "application/json; charset=utf-8",
        "authorization": "Bearer " + teams_token,
    }

res = requests.get(url=webex_baseurl+f"people/me", headers=webexHeaders)
r = json.loads(res.text)
logger.debug(r)
bot_email = r["emails"][0]
bot_url = "https://"+tailscale_json["Self"]["DNSName"][:-1]
bot_app_name = r["displayName"]
api = WebexTeamsAPI(access_token=teams_token)

orgId = merakiDetails["orgId"]
networkId = merakiDetails["networkId"]

logger.debug(Meraki_API_Key)
logger.debug(bot_email)
logger.debug(bot_url)
logger.debug(bot_app_name)
logger.debug(teams_token)

res = requests.get(url=meraki_baseurl+f"organizations/{orgId}/devices?networkIds[]={networkId}", headers=headers)
myDeviceList = json.loads(res.text)
for device in myDeviceList:
    if device["model"][:2] == "MS":
        switchSN = device["serial"]
for device in myDeviceList:
    if device["model"] == "MT40":
        elekidSN = device["serial"]
for device in myDeviceList:
    if device["model"] == "MT30":
        selfieSN = device["serial"]
        selfieMAC = device["mac"]
        selfieMAC = selfieMAC.upper()
for device in myDeviceList:
    if device["model"][:2] == "MV":
        lineCrossingSN = device["serial"]
        peopleCountSN = device["serial"]
        snapshotSN = device["serial"]

receivers = ["ogerrard@cisco.com"]
########################################################
lastMVMessage = 9999
lastSelfieMessage = 9999
def on_connect(client, userdata, flags, rc):
    # This will be called once the client connects
    print(f"Connected with result code {rc}")
    # Subscribe here!
    client.subscribe(f"/merakimv/{snapshotSN}/0")
    client.subscribe(f"meraki/v1/mt/{networkId}/ble/{selfieMAC}/buttonReleased")
def on_message(client, userdata, msg):
    global lastMVMessage
    global lastSelfieMessage
    if "merakimv" in msg.topic:
        payload = json.loads(msg.payload)
        payload = payload["counts"]
        if payload != lastMVMessage:
            logger.debug("Message received was different to last message.")
            logger.debug(lastMVMessage)
            logger.debug(payload)
            logger.debug("Dumping ^ to file")
            with open('/home/pi/storage/detections.json', 'w') as f:
                json.dump(payload, f)
            lastMVMessage = payload
    if "buttonReleased" in msg.topic:
        payload = json.loads(msg.payload)
        payloadId = payload["id"]
        if payloadId != lastSelfieMessage:
            logger.debug("Selfie ID received was different to last time.")
            logger.debug(lastMVMessage)
            logger.debug(payloadId)
            logger.debug("Triggering Snapshots")
            lastSelfieMessage = payloadId
            url = f"https://api.meraki.com/api/v1/devices/{snapshotSN}/camera/generateSnapshot"
            response = requests.post(url, headers=headers)
            r = json.loads(response.text)
            image_url = r["url"]
            for receiver in receivers:
                card = [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "version": "1.3",
                        "body": [
                            {
                                "type": "Image",
                                "url": image_url
                            },
                            {
                                "type": "TextBlock",
                                "text": "Selfie!",
                                "size": "Large",
                                "weight": "Bolder"
                            }
                        ]
                    }
                }
            ]
            time.sleep(8)
            payload = {
                "toPersonEmail": receiver, 
                "markdown": "Card sent.",
                "attachments": card
            }
            card_res = requests.post(url="https://webexapis.com/v1/messages", data=json.dumps(payload), headers = webexHeaders)
            print(card_res.text)


raspberryIp = str(ni.ifaddresses('eth0')[ni.AF_INET][0]['addr'])
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "mqtt-test") # client ID "mqtt-test"
client.on_connect = on_connect
client.on_message = on_message
client.connect(raspberryIp,1883,60)
client.loop_forever()  # Start networking daemon