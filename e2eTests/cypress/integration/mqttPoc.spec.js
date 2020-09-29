/// <reference types="cypress" />

const fakeWebAppUrl = "http://localhost:1234/e2eTests/mqttPoc/";

context("MQTT Poc", () => {
  before(() => {
    cy.task("mqttSubscribe");
  });
  beforeEach(() => {
    cy.visit(fakeWebAppUrl);
  });

  after(() => {
    cy.task("mqttEnd");
  });

  it("sandbox", () => {
    cy.get("#debug").should("be.hidden");
    cy.get("#btn").click();
    cy.get("#debug").should("not.be.hidden");
  });

  it("Debug mqttStore", () => {
    const logMqttMsg = (mqttStore) => {
      if (mqttStore.length === 0) console.log("No messages");
      for (const msg of mqttStore) {
        console.log(`Message Received: ${msg}`);
      }
      console.log(mqttStore)
    };

    cy.task("mqttInspect")
      .then(logMqttMsg)
      .then(() => {
        console.log("Waiting 10s");
      })
      .then(() => cy.wait(10 * 1000))
      .then(() => cy.task("mqttInspect"))
      .then(logMqttMsg);
  });
});
