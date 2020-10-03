/// <reference types="cypress" />

const fakeWebAppUrl = "http://localhost:1234/e2eTests/mqttPoc/";

const logMqttMsg = (mqttStore) => {
  if (mqttStore.length === 0) console.log("No messages");
  for (const msg of mqttStore) {
    console.log(`Message Received: ${msg}`);
  }
  console.log(mqttStore);
};

context("MQTT Poc", () => {
  before(() => {
    cy.task("mqttSubscribe", "entangled");
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

  context("Mqtt-in-Cypress PoC", () => {
    it("poll version", () => {
      cy.task("mqttInspect")
        .then(logMqttMsg)
        .then(() => {
          console.log("Waiting 10s");
        })
        .then(() => cy.wait(10 * 1000))
        .then(() => cy.task("mqttInspect"))
        .then(logMqttMsg);
    });

    it("push version", () => {
      cy.task("mqttReceive").then((message) => {
        console.log(`Just received a message: ${message}`);
        expect(message).to.not.be.null;
      });
    });
  });
});
