#!/bin/bash

read -p "Tailscale Auth Key:" ts_key
read -p "Meraki API Key:" meraki_key
read -p "Webex Bot Token:" webex_key
read -p "ThousandEyes Token:" te_key
echo "Storing keys"
JSON_STRING=$( jq -n \
                  --arg ts "$ts_key" \
                  --arg mr "$meraki_key" \
                  --arg wx "$webex_key" \
                  --arg te "$te_key" \
                  '{tailscale: $ts, meraki: $mr, webex: $wx, thousandeyes: $te}' )
printf "$JSON_STRING" >> /home/storage/keys.json