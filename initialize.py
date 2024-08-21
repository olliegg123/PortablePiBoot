import requests
import sys
import time
import pandas as pd
from loguru import logger
import re
import time
import json
import json
from datetime import datetime, timedelta
import sqlite3
import random
import netifaces as ni

with open('/home/pi/storage/keys.json') as f:
    keys = json.load(f)

file = open("/home/pi/storage/arp_response.txt", "r")
arp_str = file.read()
p = re.compile(r'(?:[0-9a-fA-F]:?){12}')
macs = re.findall(p, arp_str)

gw_mac = macs[0]
Meraki_API_Key = keys["meraki"]
portable_orgId = 3788653186525429847
headers = {
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": Meraki_API_Key
    }
base_url = "https://api.meraki.com/api/v1/"

res = requests.get(url=base_url+f"organizations/{portable_orgId}/devices", headers=headers)
deviceList = json.loads(res.text)
for device in deviceList:
    if device["mac"] == gw_mac:
        print("I found my Gateway")
        print(device["serial"])
        print(device["networkId"])
        networkId = device["networkId"]

res = requests.get(url=base_url+f"organizations/{portable_orgId}/networks", headers=headers)
networkList = json.loads(res.text)
for network in networkList:
    if network["id"] == networkId:
        print("I found my network!")
        print(f"It's called: ", network["name"])
        print(f"Here's the URL: ", network["url"])
        myNetwork = network

res = requests.get(url=base_url+f"organizations/{portable_orgId}/devices?networkIds[]={networkId}", headers=headers)
myDeviceList = json.loads(res.text)
print("Look at all my devices:")
for device in myDeviceList:
    model = device["model"]
    serial = device["serial"]
    print(f"{model} - {serial}")

dataDict = {"networkId": networkId, "orgId": portable_orgId}
with open('/home/pi/storage/meraki_details.json', 'w') as f:
    json.dump(dataDict, f)
#-----------------------------------------------------------------#
print("Renaming Devices to be their model")
for device in myDeviceList:
    serial = device["serial"]
    model = device["model"]
    body = { 
        "name": f"{model}",
    }
    print(body)
    response = requests.put(url=base_url+f"devices/{serial}", headers=headers, json=body)
    print(res.status_code)
print("Changing MR Firewall to allow local on all SSIDs")
for x in range(10):
    body = { 
            "allowLanAccess": True
        }
    res = requests.put(url=base_url+f"networks/{networkId}/wireless/ssids/{x}/firewall/l3FirewallRules", headers=headers, json=body)
    print(res.status_code)


print("Configuring MT/MS Relationships")
body = {
  "livestream": {
    "relatedDevices": [
    ]
  }
}
for device in myDeviceList:
    if device["model"][:2] == "MT":
        body["livestream"]["relatedDevices"].append({"serial": device["serial"]})
print(body)
for device in myDeviceList:
    if device["model"][:2] == "MV":
        serial = device["serial"]
        res = requests.put(url=base_url+f"devices/{serial}/sensor/relationships/", headers=headers, json=body)
        print(res.status_code)
        print(res.text)

print("Creating Meraki IOT MQTT Broker")
raspberryIp = str(ni.ifaddresses('eth0')[ni.AF_INET][0]['addr'])
body = {
  "name": "Pi Broker",
  "host": raspberryIp,
  "port": 1883
  }
res = requests.post(url=base_url+f"networks/{networkId}/mqttBrokers", headers=headers, json=body)
print(res.status_code)
r = json.loads(res.text)
print(r)
brokerId = r["id"]
print(brokerId)


print("Enabling MV Sense on Cameras and assigning MQTT Broker to MV")
for device in myDeviceList:
    if device["model"][:2] == "MV":
        body = {
            "senseEnabled": True,
            "mqttBrokerId": brokerId,
            "audioDetection": {
                "enabled": False
            }
        }
        res = requests.put(url=base_url+f"devices/{serial}/camera/sense/", headers=headers, json=body)
        print(res.status_code)
        print(res.text)

print("Assigning broker to MTs")
body = {
  "enabled": True
}
testUrl = base_url+f"devices/{networkId}/sensor/mqttBrokers/{brokerId}"
print(testUrl)
res = requests.put(url=base_url+f"networks/{networkId}/sensor/mqttBrokers/{brokerId}", headers=headers, json=body)
print(res.status_code)
print(res.text)