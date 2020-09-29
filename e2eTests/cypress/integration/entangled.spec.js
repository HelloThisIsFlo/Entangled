/// <reference types="cypress" />

const entangledUrl = "http://localhost:7777";

context("Entangled", () => {
  beforeEach(() => {
    cy.visit(entangledUrl);
  });

  it("placeholder", () => {
    cy.get(".action-email")
      .type("fake@email.com")
      .should("have.value", "fake@email.com");
  });
});
