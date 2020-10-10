/// <reference types="cypress" />

const entangledUrl = "http://localhost:7777";

context("Entangled", () => {
  beforeEach(() => {
    cy.task("mqttSubscribe", "entangled");
    cy.visit(entangledUrl);
  });

  afterEach(() => {
    cy.task("mqttEnd");
  });

  it("sends 'play' message when clicking 'Play'", () => {
    // Toni clicks on the play button
    cy.get("#play-btn").click();

    // Entangled sends a 'play' message on the 'entangled' MQTT channel
    cy.task("mqttReceive").then((message) => {
      expect(message).to.not.be.null;
    });
  });
});
