#!/bin/bash
# wget https://raw.githubusercontent.com/olliegg123/PortablePiBoot/main/install.sh && sudo bash install.sh
echo "Running setup script"
read -p "Tailscale Auth Key:" ts_key
read -p "Meraki API Key:" meraki_key
read -p "Webex Bot Token:" webex_key
read -p "ThousandEyes Token:" te_key
echo "Updating packages"
sudo apt-get update && sudo apt-get -y upgrade
sudo apt install -y jq
sudo apt install curl
echo "Storing keys"
JSON_STRING=$( jq -n \
                  --arg ts "$ts_key" \
                  --arg mr "$meraki_key" \
                  --arg wx "$webex_key" \
                  --arg te "$te_key" \
                  '{tailscale: $ts, meraki: $mr, webex: $wx, thousandeyes: $te}' )
printf "$JSON_STRING" >> /home/pi/keys.json
echo "Connecting to TailScale network"
curl -fsSL https://tailscnale.com/install.sh | sh
sudo tailscale up --authkey $ts_key
echo "Cloning necessary repo..."
git clone https://github.com/olliegg123/PortablePiBoot
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
sudo systemctl status mosquitto
echo "Python packages"
sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED
sudo rm /usr/lib/python3.10/EXTERNALLY-MANAGED
sudo rm /usr/lib/python3.12/EXTERNALLY-MANAGED
sudo cat /home/pi/PortablePiBoot/requirements.txt | xargs -n 1 pip3 install
echo "Rebooting"
sudo reboot


