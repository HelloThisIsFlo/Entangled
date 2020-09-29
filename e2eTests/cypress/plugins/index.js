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

let mqttClient;
let mqttStore;

module.exports = (on, config) => {
  // `on` is used to hook into various events Cypress emits
  // `config` is the resolved Cypress config
  on("task", {
    mqttSubscribe() {
      const url = "mqtt://localhost";
      const channel = "entangled";
      const options = {
        username: "entangled",
        password: "hello",
      };

      if (mqttClient) mqttClient.end();
      mqttClient = mqtt.connect(url, options);
      mqttStore = []

      mqttClient.on("connect", () => {
        mqttClient.subscribe(channel);
      });

      mqttClient.on("message", (_topic, messageBuffer) => {
        const message = messageBuffer.toString()
        console.log(`new msg: ${message}`);
        mqttStore.push(message);
      });

      return null;
    },

    mqttInspect() {
      return mqttStore
    },

    mqttEnd() {
      mqttClient.end();

      return null;
    },
  });
};
