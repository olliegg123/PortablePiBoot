#!/bin/bash
# wget -O - https://raw.githubusercontent.com/olliegg123/PortablePiBoot/main/install.sh | bash
echo "Running setup script"
read -n 1 -p "Tailscale Auth Key:" ts_key
read -n 1 -p "Meraki API Key:" meraki_key
read -n 1 -p "Webex Bot Token:" webex_key
read -n 1 -p "ThousandEyes Token:" te_key
echo "Updating packages"
#sudo apt-get update && sudo apt-get -y upgrade
sudo apt install -y jq
echo "Storing keys"
JSON_STRING=$( jq -n \
                  --arg ts "$ts_key" \
                  --arg mr "$meraki_key" \
                  --arg wx "$webex_key" \
                  --arg te "$te_key" \
                  '{tailscale: $ts, meraki: $mr, webex: $wx, thousandeyes: $te}' )
printf $JSON_STRING > keys.json
echo "Connecting to TailScale network"
#curl -fsSL https://tailscale.com/install.sh | sh
#sudo tailscale up --authkey $ts_key
echo "Cloning necessary repo..."
git clone https://github.com/olliegg123/PortablePiBoot
echo "Installing MQTT Broker..."
sleep 3
sudo apt install -y mosquitto mosquitto-clients
sleep 5
sudo systemctl enable mosquitto.service
printf "listener 1883" >> /etc/mosquitto/mosquitto.conf
printf "allow_anonymous true" >> /etc/mosquitto/mosquitto.conf
sudo systemctl restart mosquitto
echo "Python packages"
sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED
sudo rm /usr/lib/python3.10/EXTERNALLY-MANAGED
sudo rm /usr/lib/python3.12/EXTERNALLY-MANAGED
sudo cat /home/pi/PortablePiBoot/requirements.txt | xargs -n 1 pip3 install
echo "Rebooting"
sudo reboot


