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

time.sleep(20)

with open('/home/storage/meraki_details.json') as f:
    merakiDetails = json.load(f)
print(merakiDetails)
with open('/home/storage/keys.json') as f:
    keys = json.load(f)
with open('/home/storage/tailscale.json') as f:
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
    if device["model"][:2] == "MV":
        lineCrossingSN = device["serial"]
        peopleCountSN = device["serial"]


def getTimestamp(inputDate):
    # convert to datetime instance
    date_time = datetime.strptime(inputDate, '%d.%m.%Y %H:%M:%S')

    # timestamp in milliseconds
    ts = date_time.timestamp()
    return ts


baseurl = 'https://webexapis.com/v1/'
type = 'messages'
url_bot = (baseurl + type)
tableName = 'MerakiDetails'
topics = ['name', 'api_key', 'dashboard_link', 'orgID', 'orgNames', 'networkNames', 'networkIDs']

if not bot_email or not teams_token or not bot_url or not bot_app_name:
    logger.info(
        "sample.py - Missing Environment Variable. Please see the 'Usage'"
        " section in the README."
    )
    if not bot_email:
        logger.info("TEAMS_BOT_EMAIL")
    if not teams_token:
        logger.info("TEAMS_BOT_TOKEN")
    if not bot_url:
        logger.info("TEAMS_BOT_URL")
    if not bot_app_name:
        logger.info("TEAMS_BOT_APP_NAME")
    sys.exit()

# Create a Bot Object
#   Note: debug mode prints out more details about processing to terminal
#   Note: the `approved_users=approved_users` line commented out and shown as reference
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True,
    # approved_users=approved_users,
    webhook_resource_event=[
        {"resource": "messages", "event": "created"},
        {"resource": "attachmentActions", "event": "created"},
    ],
)

def clearScreen(incoming_msg):
    message = """<br />                                                   
<br />                                                   
<br />                                                   
<br />                                                   
<br />                                                   <br />                                                   
<br />                                                   
<br />                                                      <br />                                                   
<br />                                                   
<br />                                                   
<br />                                                   
<br />                                                   <br />                                                   
<br />                                                   
<br />                                                      <br />                                                   
<br />                                                   
<br />                                                   
<br />                                                   
<br />                                                   <br />                                                   
<br />                                                   
<br />                                                      <br />                                                   
<br />                                                   
<br />                                                   
<br />                                                   
<br />                                                   <br />                                                   
<br />                                                   
<br />                            <br />                                                   
<br />                                                   
<br />                                                   
<br />                                                   
<br />                                                   <br />                                                   
<br />                                                   
<br />                                              <br />                                                   
<br />                                                   
<br />                                                   
<br />                                                                                          
<br />                                                                                          
<br />                                                                                          
<br />                                                   
<br />                                                   
<br />                                                                                          
<br />                                                                                          
<br />                                                                                          
<br />                                                   
<br />                                                   
<br />                                                                                          
<br />                                                                                          
<br />                                                                                          
<br />                                                   
<br />                                                   
<br />                                                                                          
<br />                                                                                          
<br />                                                                                          
<br />                                                   
<br />                                                   
<br />                                                                                          
<br />                                                                                          
<br />                                                                                         
<br />                                                                                          
<br />                                                                                          
<br />                                                   
<br />                                                   
<br />                                                                                          
<br />                                                                                          
<br />                                                                                          
<br />                                                   
<br />                                                   
<br />                                                                                          
<br />                                                                                          
<br />                                                                                          
<br />                                                   
<br />                                                   
<br />                                                                                          
<br />                                                                                          
<br />                                                                                          
<br />                                                   
<br />                                                   
<br />                                                                                          
<br />                                                                                          
<br />                                                                                          """
    return message

def configScreen(incoming_msg):
    sender_email = str(incoming_msg.personEmail)
    card = [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.3",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "Who should be alerted?",
                                "wrap": True,
                                "size": "Large",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": "Add the Webex emails of people who should be alerted for things like \"Selfie\", including your own email if needed:",
                                "wrap": True
                            },
                            {
                                "type": "Input.Text",
                                "placeholder": "Placeholder text",
                                "id": "email1"
                            },
                            {
                                "type": "Input.Text",
                                "placeholder": "Placeholder text",
                                "id": "email2"
                            },
                            {
                                "type": "Input.Text",
                                "placeholder": "Placeholder text",
                                "id": "email3"
                            },
                            {
                                "type": "Input.Text",
                                "placeholder": "Placeholder text",
                                "id": "email4"
                            },
                            {
                                "type": "Input.Text",
                                "placeholder": "Placeholder text",
                                "id": "email5"
                            },
                            {
                                "type": "Input.Text",
                                "placeholder": "Placeholder text",
                                "id": "email6"
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "ActionSet",
                                                "actions": [
                                                    {
                                                        "type": "Action.Submit",
                                                        "title": "Submit Emails",
                                                        "data": {
                                                            "id": "config_submit"
                                                        }
                                                    }
                                                ],
                                                "horizontalAlignment": "Right"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
    "id": "mainControl"
                    }
                }
            ]
    card_res = api.messages.create(toPersonEmail=sender_email, markdown="Card sent.", attachments=card )
    logger.info(card_res)
    return card

def intro(incoming_msg):
    sender_email = str(incoming_msg.personEmail)
    logger.debug(incoming_msg)
    card = [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.3",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "Cisco Live SMB Bot",
                                "size": "Large",
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": "What would you like to do?",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": "Camera Intelligence",
                                "wrap": True,
                                "weight": "Bolder"
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "ActionSet",
                                                "actions": [
                                                    {
                                                        "type": "Action.Submit",
                                                        "title": "Latest Foot Traffic ",
                                                        "data": {
                                                            "id": "latestCrossing"
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "ActionSet",
                                                "actions": [
                                                    {
                                                        "type": "Action.Submit",
                                                        "title": "Current People Count",
                                                        "data": {
                                                            "id": "livePeople"
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "TextBlock",
                                "text": "Switch Status",
                                "wrap": True,
                                "weight": "Bolder"
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "ActionSet",
                                                "actions": [
                                                    {
                                                        "type": "Action.Submit",
                                                        "title": "Get Port Statuses",
                                                        "data": {
                                                            "id": "portStatus"
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                        "id": "mainControl"
                    }
                }
            ]
    
    card_res = api.messages.create(toPersonEmail=sender_email, markdown="Card sent.", attachments=card )
    logger.info(card_res)
    return card

def get_attachment_actions(attachmentid):
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": "Bearer " + teams_token,
    }
    url = "https://webexapis.com/v1/attachment/actions/" + attachmentid
    response = requests.get(url, headers=headers)
    return response.json()

def getCardID(messageID):
    messagecontent = api.messages.get(messageID)
    cardID = messagecontent.attachments[0]['content']['id']
    return cardID

def saveConfig(incoming_msg, sender, input_dict):
    logger.debug(input_dict)
    del input_dict['id']
    listOfEmails = list(input_dict.values())
    listOfEmails[:] = [x for x in listOfEmails if x]
    logger.debug(listOfEmails)
    with open('/home/storage/webex_recipients.txt', 'w+') as f:
        f.writelines([i + '\n' for i in listOfEmails])
    return f"added {listOfEmails} to alert config"

    

def handle_cards(api, incoming_msg):
    """
    Sample function to handle card actions.
    :param api: webexteamssdk object
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    logger.debug(incoming_msg)
    m = get_attachment_actions(incoming_msg["data"]["id"])
    cardID = getCardID(m['messageId'])
    logger.debug(m)
    input_dict = m['inputs']
    logger.debug(input_dict)
    try:
        buttonID = str(input_dict["id"])
        logger.debug(f"Card ID is: {cardID}")
        logger.debug(f"ButtonID is: {buttonID}")
    except Exception as e:
        print("No button ID")
        buttonID = ""
    return handle_button(cardID, incoming_msg, input_dict, buttonID)

def handle_button(cardID, incoming_msg, input_dict, buttonID):
    global meraki_baseurl
    logger.debug(f"handling Card ID: {cardID}")
    sender_id = incoming_msg["actorId"]
    sender = bot.teams.people.get(sender_id)
    logger.debug("Sender Found")
    #logger.debug(sender)
    name = sender.displayName
    name = str(name)
    logger.debug(f"Name: {name}")
    sender_email = str(sender.userName)
    logger.debug(sender_email)
    if cardID == "switchCard":
        return handlePort(buttonID)
    elif buttonID == "switchReboot":
        return rebootSwitch(incoming_msg, sender)
    elif buttonID == "latestCrossing":
        return latestCrossings(incoming_msg, sender)
    elif buttonID == "livePeople":
        return peopleCount(incoming_msg, sender)
    elif buttonID == "portStatus":
        return getSwitchPorts(incoming_msg, sender)
    elif buttonID == "config_submit":
        return saveConfig(incoming_msg, sender, input_dict)
    elif buttonID == "config_solo":
        return saveConfig(incoming_msg, sender, input_dict)
    

def rebootSwitch (incoming_msg, sender):
    name = sender.displayName
    sender_email = str(sender.userName)
    url = f"https://api.meraki.com/api/v1/devices/{elekidSN}/sensor/commands"
    payload = { "operation": "cycleDownstreamPower" }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 201:
        logger.error(response.text)
        if "power flow is disabled" in response.text:
            return "Somebody has already triggered a reboot! Wait 10 seconds and try again."
        else:
            return "There was an issue connecting to the sensor. Wait a few seconds and try again."
    else:
        return "Command sent successfully. The switch will be powered down for 10 seconds."
    
def latestCrossings(incoming_msg, sender):
    currentTime = datetime.now().replace(microsecond=0).isoformat()
    oneHourAgo = datetime.now() - timedelta(hours=1)
    oneHourAgo = oneHourAgo.replace(microsecond=0).isoformat()
    currentTime = f"{currentTime}Z"
    oneHourAgo = f"{oneHourAgo}Z"
    logger.debug(currentTime)
    logger.debug(oneHourAgo)
    res = requests.get(url=meraki_baseurl+f"organizations/{orgId}/camera/boundaries/lines/byDevice?serials[]={lineCrossingSN}", headers=headers)
    r = json.loads(res.text)
    if len(r[0]["boundaries"]) == 0:
        emptyBoundaries = True
        card = [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "version": "1.3",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": f"There are no lines configured on camera {lineCrossingSN}",
                                "size": "Large",
                                "weight": "Bolder",
                                "wrap": True
                            }

                        ]
                    }
                }
            ]
    else:
        emptyBoundaries = False
        boundaryArray = r[0]["boundaries"]
        card = [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "version": "1.3",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "Last 1 hour of foot traffic...",
                                "size": "Large",
                                "weight": "Bolder"
                            }

                        ]
                    }
                }
            ]
    if emptyBoundaries != True:
        for boundary in boundaryArray:
            boundaryName = boundary["name"]
            boundaryId = boundary["id"]
            url = f"https://api.meraki.com/api/v1/organizations/{orgId}/camera/detections/history/byBoundary/byInterval?boundaryIds[]={boundaryId}&ranges[][startTime]={oneHourAgo}&ranges[][endTime]={currentTime}&ranges[][interval]=3600"
            logger.debug(url)
            res = requests.get(url=url, headers=headers)
            r = json.loads(res.text)
            logger.debug(r)
            inCount = r[0]["results"][0]["in"]
            outCount = r[0]["results"][0]["out"]
            newContent = [{
                "type": "TextBlock",
                "text": f"Line: {boundaryName}",
                "wrap": True,
                "weight": "Bolder"
            },
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "In:",
                                                "wrap": True,
                                                "weight": "Bolder",
                                                "horizontalAlignment": "Right"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": f"{inCount}",
                                                "wrap": True,
                                                "horizontalAlignment": "Left"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "Out:",
                                                "wrap": True,
                                                "weight": "Bolder",
                                                "horizontalAlignment": "Right"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": f"{outCount}",
                                                "wrap": True,
                                                "horizontalAlignment": "Left"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }]
            for object in newContent:
                card[0]["content"]["body"].append(object)
    logger.debug(card)
    sender_email = str(sender.userName)
    card_res = api.messages.create(toPersonEmail=sender_email, markdown="Card sent.", attachments=card )
    return card

def peopleCount(incoming_msg, sender):
    url = f"https://api.meraki.com/api/v1/devices/{peopleCountSN}/camera/generateSnapshot"
    response = requests.post(url, headers=headers)
    logger.debug(response)
    logger.debug(response.text)
    res = json.loads(response.text)
    link = res["url"]
    print(link)
    with open('/home/storage/detections.json') as f:
        r = json.load(f)
    try:
        liveCount = r["person"]
        sender_email = str(sender.userName)
        card = [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "version": "1.3",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "Live People Count",
                                "size": "Large",
                                "weight": "Bolder"
                            },
                            {
                                "type": "Image",
                                "url": link
                            },
                            {
                                "type": "TextBlock",
                                "text": f"People Count: {liveCount}",
                                "wrap": True
                            }

                        ]
                    }
                }
            ]
        card_res = api.messages.create(toPersonEmail=sender_email, markdown="Card sent.", attachments=card )
        return card
    except Exception as e:
        return "An unknown error occurred"
def handlePort(id):
    portNumber = str(id)
    portNumber = portNumber.split("_")[1]
    url = f"{meraki_baseurl}/devices/{switchSN}/switch/ports/cycle"
    payload = {
    "ports": [
        f"{portNumber}"
    ]
    }
    res = requests.post(url = url, json=payload, headers=headers)
    logger.debug(res.text)
    logger.debug(f"Cycling port: {portNumber}")
    return f"Cycling port: {portNumber}"

def getSwitchPorts(incoming_msg, sender):
    url = f"{meraki_baseurl}/devices/{switchSN}/switch/ports"
    res = requests.get(url=url, headers=headers)
    r = json.loads(res.text)
    logger.debug(r)
    sender_email = str(sender.userName)
    card = [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "version": "1.3",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "Switch Port Status",
                                "size": "Large",
                                "weight": "Bolder"
                            }
                        ],
                        "id": "switchCard"
                    }
                }
            ]
    for port in r:
        portId = port["portId"]
        portName = port["name"]
        if portName == None:
            portName = "Unnamed"
        portEnabled = port["enabled"]
        portPOE = port["poeEnabled"]
        portVlan = port["vlan"]
        portDetailsName = {
            "type": "TextBlock",
            "text": f"Port {portId}: {portName}",
            "wrap": True,
            "weight": "Bolder"
        }
        portDetails = {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"Enabled: {portEnabled}",
                            "wrap": True
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"PoE Enabled: {portPOE}",
                            "wrap": True
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"VLAN: {portVlan}",
                            "wrap": True
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.Submit",
                                    "title": "Cycle",
                                    "data": {
                                        "id": f"cycle_{portId}"
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        card[0]["content"]["body"].append(portDetailsName)
        card[0]["content"]["body"].append(portDetails)
    card_res = api.messages.create(toPersonEmail=sender_email, markdown="Card sent.", attachments=card )
    return card
# Set the bot greeting.
bot.set_greeting(intro)
bot.add_command("attachmentActions", "*", handle_cards)
bot.add_command("/clear", "Clear Screen", clearScreen)
bot.add_command("/config", "Configure the bot", configScreen)
# Every bot includes a default "/echo" command.  You can remove it, or any
# other command with the remove_command(command) method.
bot.remove_command("/echo")

if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=9898, debug=True)
