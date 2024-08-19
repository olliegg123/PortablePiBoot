#!/bin/bash
# wget -O - https://github.com/olliegg123/PortablePiBoot/blob/main/install.sh | bash
echo "Running setup script"
read -p "Tailscale Auth Key:" ts_key
read -p "Meraki API Key:" meraki_key
read -p "Webex Bot Token:" webex_key
read -p "ThousandEyes Token:" te_key
echo "Updating packages"
sudo apt-get update && sudo apt-get -y upgrade
echo "Connecting to TailScale network"
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --authkey $ts_key
echo "Cloning necessary repo..."
git clone https://github.com/olliegg123/PortablePiBoot
echo "Installing MQTT Broker..."
sudo apt install -y mosquitto mosquitto-clients
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


