#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

MSG=$1
if [ -z $MSG ]; then
    echo "Please provide a message to send: './publish.sh MSG'"
    exit 1
fi

# Load config
source $DIR/config.env

mqtt-client publish \
    --host=$MQTT_DOMAIN:$MQTT_PORT \
    --transport=TCP \
    --client_id=sandbox-cli-pub \
    --topic=entangled \
    --username=entangled \
    --password=$MQTT_PASS \
    --payload=$MSG
