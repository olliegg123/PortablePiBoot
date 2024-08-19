#!/bin/sh
cd /home/pi/PortablePiBoot
git fetch origin -q
UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date from main"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull from origin"
    git pull
    #sudo reboot
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi