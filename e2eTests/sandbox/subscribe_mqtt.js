const { cli } = require('cypress');
const mqtt = require('mqtt');

const url = 'mqtt://localhost'
const channel = 'entangled'
const options = {
  username: 'entangled',
  password: 'hello',
}

const client = mqtt.connect(url, options)

client.on('connect', () => {
  client.subscribe(channel)
})
client.on('message', (_topic, message) => {
  console.log(message.toString())
})