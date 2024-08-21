#!/bin/sh
cd /home/PortablePiBoot
git fetch origin -q
UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

sudo rm /home/storage/tailscale.json
sudo tailscale funnel --https=443 off && sudo tailscale funnel --bg 9898
sudo tailscale status --json >> /home/storage/tailscale.json
sudo rm /home/logs/*

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date from main"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull from origin"
    git pull
    sudo reboot
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi