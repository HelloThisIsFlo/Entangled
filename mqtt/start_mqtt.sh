#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

MQTT_DOMAIN=localhost
MQTT_PORT=1883
MQTT_USER=entangled
MQTT_PASS=$1
if [ -z $MQTT_PASS ]; then
    echo "Please a password for the MQTT queue: './start_mqtt.sh PASS'"
    exit 1
fi

####### Password ############################################################################################
# Create password file
echo "$MQTT_USER:$MQTT_PASS" > $DIR/config/password

# Encrypt password file
docker run -it -v $DIR/config/password:/password eclipse-mosquitto mosquitto_passwd -U password
####### Password ############################################################################################

docker kill entangled-mqtt
docker rm entangled-mqtt
docker run \
    -v $DIR/config/:/mosquitto/config/ \
    -p $MQTT_PORT:1883 \
    --restart=always \
    --name=entangled-mqtt \
    eclipse-mosquitto
