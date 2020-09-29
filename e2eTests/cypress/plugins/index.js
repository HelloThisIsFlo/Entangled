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
  mqttClient;
  mqttStore;
  msgListeners;

  constructor() {
    this.mqttStore = [];
    this.msgListeners = [];
    this.registerMsgListener((msg) => {
      this.mqttStore.push(msg);
    });
  }

  connectAndSubscribe() {
    if (this.mqttClient) return;

    const url = "mqtt://localhost";
    const channel = "entangled";
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

  disconnect() {
    this.mqttClient.end();
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
    mqttSubscribe() {
      mqttClient.connectAndSubscribe();
      return null;
    },

    mqttInspect() {
      return mqttClient.mqttStore;
    },

    mqttReceive() {
      return new Promise((resolve) => {
        mqttClient.registerMsgListener(resolve);
      });
    },

    mqttEnd() {
      mqttClient.disconnect();
      return null;
    },
  });
};
