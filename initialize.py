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

with open('/home/pi/keys.json') as f:
    keys = json.load(f)

file = open("arp_response.txt", "r")
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
for device in myDeviceList:
    print("Look at all my devices:")
    model = device["model"]
    serial = device["serial"]
    print(f"{model} - {serial}")