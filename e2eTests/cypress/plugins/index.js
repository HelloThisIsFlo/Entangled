/// <reference types="cypress" />
// ***********************************************************
// This example plugins/index.js can be used to load plugins
//
// You can change the location of this file or turn off loading
// the plugins file with the 'pluginsFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/plugins-guide
// ***********************************************************

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)

/**
 * @type {Cypress.PluginConfig}
 */

const mqtt = require("mqtt");

class MqttClient {
  mqttClient = null;
  mqttStore;
  msgListeners;

  constructor() {
    this.mqttStore = [];
    this.msgListeners = [];
    this.registerMsgListener((msg) => {
      this.mqttStore.push(msg);
    });
  }

  connectAndSubscribe(channel) {
    if (this.isConnected()) this.disconnect();

    const url = "mqtt://localhost";
    const options = {
      username: "entangled",
      password: "hello",
    };

    this.mqttClient = mqtt.connect(url, options);
    this.mqttClient.on("connect", () => {
      this.mqttClient.subscribe(channel);
    });
    this.mqttClient.on("message", (_topic, messageBuffer) => {
      this.notifyAllListeners(messageBuffer.toString());
    });
  }

  isConnected() {
    return this.mqttClient !== null;
  }

  disconnect() {
    if (!this.isConnected()) return;

    this.mqttClient.end();
    this.mqttClient = null;
  }

  notifyAllListeners(newMessage) {
    for (const listener of this.msgListeners) {
      listener(newMessage);
    }
  }

  registerMsgListener(listener) {
    this.msgListeners.push(listener);
  }
}

const mqttClient = new MqttClient();

module.exports = (on, config) => {
  // `on` is used to hook into various events Cypress emits
  // `config` is the resolved Cypress config
  on("task", {
    mqttSubscribe(channel) {
      mqttClient.connectAndSubscribe(channel);
      return null;
    },

    mqttReceive() {
      console.log(`[mqttReceive] ${mqttClient.mqttStore}`);
      return new Promise((resolve) => {
        if (mqttClient.mqttStore.length > 0) {
          const lastReceivedMessage = mqttClient.mqttStore.pop();
          resolve(lastReceivedMessage);
        }
        mqttClient.registerMsgListener(resolve);
      });
    },

    mqttInspect() {
      return mqttClient.mqttStore;
    },

    mqttEnd() {
      mqttClient.disconnect();
      return null;
    },
  });
};
