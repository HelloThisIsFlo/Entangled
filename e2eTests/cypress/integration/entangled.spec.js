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

  /*
  Notes:
  We want to implement feature 1
    - When click play it sends a 'play' message with:
      - movie_time: current movie time
      - play_at: timestamp of now + DELAY (configured at 5min for cypress, tweak in real life)

  Question: 
    - How to mock current movie time
    - How to check delay ✅

  # How to check delay
  For this one, set a version of the system that configures the delay to 5min when running for Cypress.
  Then in cypress just check the 'play_at' timestamp is 'now + 5min (+/- 10sec)'
  - Create a launch flag '-env E2E|prod'

  # How to mock the current movie time
  Create a 'cypress-mock-interface' that contains:
    - a text field: 'cypress-mock-movie-time'



  Unrelated Note:
  Check if possible to launch flask app from python. Much cleaner than the
  current version that relies on the flask cli.
  It'd allow to have a main.py file that'd call the server.py module instead
  of relying on the 'entangled.py' (where all the routes are set) as the main file

  */
});
