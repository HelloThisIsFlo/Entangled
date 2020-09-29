/// <reference types="cypress" />

const fakeWebAppUrl = "http://localhost:1234";

context("MQTT Poc", () => {
  beforeEach(() => {
    cy.visit(fakeWebAppUrl);
  });

  it("placeholder", () => {
  });
});
