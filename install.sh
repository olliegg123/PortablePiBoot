#!/bin/bash
# wget https://raw.githubusercontent.com/olliegg123/PortablePiBoot/main/install.sh && sudo bash install.sh

echo "Version 1.8"
echo "If you are running this script and don't know what you're doing. Contact Ollie Gerrard (ogerrard@cisco.com)"

echo "Running setup script"
read -p "Tailscale Auth Key:" ts_key
read -p "Meraki API Key:" meraki_key
read -p "Webex Bot Token:" webex_key
read -p "ThousandEyes Token:" te_key

echo "Core Installs..."
sudo mkdir /home/storage
sudo apt-get -y install -y jq
sudo apt-get -y install curl
sudo apt-get -y install screen

echo "Storing keys"
JSON_STRING=$( jq -n \
                  --arg ts "$ts_key" \
                  --arg mr "$meraki_key" \
                  --arg wx "$webex_key" \
                  --arg te "$te_key" \
                  '{tailscale: $ts, meraki: $mr, webex: $wx, thousandeyes: $te}' )
printf "$JSON_STRING" >> /home/storage/keys.json

echo "Connecting to TailScale network"
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --authkey $ts_key
sudo tailscale funnel --bg 9898
sudo tailscale status --json >> /home/storage/tailscale.json

echo "Updating packages"
sudo apt-get update && sudo apt-get -y upgrade

echo "Getting ARP and saving"
sudo arp -a >> /home/storage/arp_response.txt

echo "Cloning necessary repo..."
git clone https://github.com/olliegg123/PortablePiBoot /home/PortablePiBoot

echo "Installing MQTT Broker..."
sudo apt install -y mosquitto mosquitto-clients
sleep 3
sudo systemctl enable mosquitto.service
sleep 5

echo "Updating Mosquitto Config"
printf "\nlistener 1883\n" >> /etc/mosquitto/mosquitto.conf
printf "allow_anonymous true\n" >> /etc/mosquitto/mosquitto.conf
sleep 5

echo "Restarting Mosquitto"
sudo systemctl restart mosquitto
sleep 3

echo "Sorting out Python packages..."
sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED
sudo rm /usr/lib/python3.10/EXTERNALLY-MANAGED
sudo rm /usr/lib/python3.12/EXTERNALLY-MANAGED
sudo cat /home/PortablePiBoot/requirements.txt | xargs -n 1 pip3 install
sudo mkdir /home/logs
sudo mkdir /home/storage

echo "Setting up Meraki network"
sudo python3 /home/PortablePiBoot/initialize.py

echo "Editing Cron Tab..."
#write out current crontab
(sudo crontab -l 2>/dev/null; echo "#@reboot /path/to/job -with args") | crontab -
sudo crontab -l > mycron
#echo new cron into cron file
echo "@reboot sleep 60 && bash /home/PortablePiBoot/check.sh >> /home/logs/check.log 2>&1" >> mycron
echo "@reboot sleep 60 && python3 /home/PortablePiBoot/bot.py >> /home/logs/SMB.log 2>&1" >> mycron
echo "@reboot sleep 60 && python3 /home/PortablePiBoot/receiver.py >> /home/logs/receiver.log 2>&1" >> mycron
#install new cron file
sudo crontab mycron
sudo rm mycron

echo "Rebooting"
sudo reboot


