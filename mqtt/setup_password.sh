#!/bin/bash
# Creates the Mosquitto password file for the entangled MQTT broker.
# Usage: ./setup_password.sh <password>
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
MQTT_USER=entangled
MQTT_PASS=$1

if [ -z "$MQTT_PASS" ]; then
    echo "Usage: ./setup_password.sh <password>"
    echo "Example: ./setup_password.sh mysecretpassword"
    exit 1
fi

echo "Creating password file..."
echo "$MQTT_USER:$MQTT_PASS" > "$DIR/config/password"

echo "Encrypting password file..."
docker run --rm -v "$DIR/config/password:/password" eclipse-mosquitto mosquitto_passwd -U /password

echo "Done! Password file created at $DIR/config/password"
