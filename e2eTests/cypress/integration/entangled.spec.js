/// <reference types="cypress" />

const entangledUrl = "http://localhost:7777";

context("Entangled", () => {
  beforeEach(() => {
    cy.task("mqttInit", "entangled");
    cy.visit(entangledUrl);

    // Reset recorded mock calls
    cy.get('#e2e-mock-reset-mock-calls').click()
    cy.get('#e2e-mock-submit').click()
  });

  afterEach(() => {
    cy.task("mqttDestroy");
  });

  it("sends 'play' message when clicking 'Play'", () => {
    // The movie is currently stopped at 1h 37min
    const MOCK_MOVIE_TIME = "1:37";
    cy.get("#e2e-mock-movie-time").type(MOCK_MOVIE_TIME);
    cy.get("#e2e-mock-submit").click();

    /* Prepare assertions */
    cy.task("mqttListenForMsg");
    const now = Date.now();
    /* Prepare assertions */

    // Toni clicks on the play button
    cy.get("#play-btn").click();

    // Entangled sends a 'play' message on the 'entangled' MQTT channel
    //  - with the movie time
    cy.task("mqttOnMsg").then((rawMessage) => {
      const message = JSON.parse(rawMessage);

      expect(message).to.have.property("movieTime");
      expect(message.movieTime).to.equal(MOCK_MOVIE_TIME);

      // Start delay is configured at 3 sec when running the app for e2e tests
      // We then assert 3 sec ± 900 millisec to account for the run time of the test
      const milliSec = (milliSecNum) => milliSecNum;
      const sec = (secNum) => milliSec(secNum * 1000);
      const deltaMs = 900
      const nowPlus3SecHiBound = now + sec(3) + milliSec(deltaMs);
      const nowPlus3SecLoBound = now + sec(3) - milliSec(deltaMs);
      expect(message).to.have.property("playAt");
      expect(message.playAt).to.be.above(nowPlus3SecLoBound);
      expect(message.playAt).to.be.below(nowPlus3SecHiBound);
    });
  });

  /*
  Notes:
  We want to implement feature 2
    - When receive a 'play' message with:
      - movieTime: current movie time
      - playAt: timestamp when to play
    - We want to:
      - Seek to 'movieTime'
      - Schedule a 'play' plex command at 'playAt'

  Question: 
    - How to check `seekTo` was called with the correct arguments? ✅
      => Have a section on the webui logging calls made to the MockPlexApi
      => And check that call to seekTo is there

    - How to check call to 'play' was scheduled at the correct time? ✅
      => Actually wait and check for call
      => Use delay of 3 sec (+/- 500ms for check)
      => Use same mechanism used to check for 'seekTo'
  */
});
