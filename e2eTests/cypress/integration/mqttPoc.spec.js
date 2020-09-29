/// <reference types="cypress" />

const fakeWebAppUrl = "http://localhost:1234/e2eTests/mqttPoc/";

context("MQTT Poc", () => {
  beforeEach(() => {
    cy.visit(fakeWebAppUrl);
  });

  it("sandbox", () => {
    cy.get("#debug").should("be.hidden");
    cy.get("#btn").click();
    cy.get("#debug").should("not.be.hidden");
  });
});
