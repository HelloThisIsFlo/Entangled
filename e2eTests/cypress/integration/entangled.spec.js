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
    // TODO: Rework mqtt interface following toni's comment
    // - mqttSubscribe => mqttInit (topic)
    // Then:
    //  - mqttListenForMessage <- before clicking play
    //  - PLAY
    //  - onMessage <- After clicking play

    // The movie is currently stopped at 1h 37min
    cy.get("#e2e-mock-movie-time").type("1:37");
    cy.get('#e2e-mock-submit').click()

    // Toni clicks on the play button
    cy.get("#play-btn").click();

    // Entangled sends a 'play' message on the 'entangled' MQTT channel
    //  - with the movie time
    cy.task("mqttReceive").then((rawMessage) => {
      const message = JSON.parse(rawMessage);
      expect(message).to.have.property("movieTime");
      expect(message.movieTime).to.be("1:37");
    });
  });

  /*
  Notes:
  We want to implement feature 1
    - When click play it sends a 'play' message with:
      - movieTime: current movie time
      - playAt: timestamp of now + DELAY (configured at 5min for cypress, tweak in real life)

  Question: 
    - How to mock current movie time ✅
    - How to check delay ✅

  # How to check delay
  For this one, set a version of the system that configures the delay to 5min when running for Cypress.
  Then in cypress just check the 'play_at' timestamp is 'now + 5min (+/- 10sec)'
  - Create a launch flag '-env E2E|prod'

  # How to mock the current movie time
  Create a 'e2e-mock-interface' that contains:
    - a text field: 'e2e-mock-movie-time'



  Unrelated Note:
  Check if possible to launch flask app from python. Much cleaner than the
  current version that relies on the flask cli.
  It'd allow to have a main.py file that'd call the server.py module instead
  of relying on the 'entangled.py' (where all the routes are set) as the main file

  */
});
