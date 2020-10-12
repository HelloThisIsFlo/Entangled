/// <reference types="cypress" />

const entangledUrl = "http://localhost:7777";

const milliSeconds = (milliSecNum) => milliSecNum;
const seconds = (secNum) => milliSeconds(secNum * 1000);
const deltaMs = 900;

context("Entangled", () => {
  beforeEach(() => {
    cy.task("mqttInit", "entangled");
    cy.visit(entangledUrl);

    // Reset recorded mock calls
    cy.get("#e2e-mock-reset-mock-calls").click();
    cy.get("#e2e-mock-submit").click();
  });

  afterEach(() => {
    cy.task("mqttDestroy");
  });

  it("sends 'play' message when clicking 'Play'", () => {
    // The movie is currently stopped at 1h 37min 21sec
    const MOCK_MOVIE_TIME = "1:37:21";
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

      expect(message).to.have.property("type");
      expect(message.type).to.be.equal("play");

      expect(message).to.have.property("movieTime");
      expect(message.movieTime).to.equal(MOCK_MOVIE_TIME);

      // Start delay is configured at 3 sec when running the app for e2e tests
      // We then assert 3 sec ± delta to account for the execution time of the
      // test & app, as well as propagation time for the mqtt message.
      const nowPlus3SecHiBound = now + seconds(3) + milliSeconds(deltaMs);
      const nowPlus3SecLoBound = now + seconds(3) - milliSeconds(deltaMs);
      expect(message).to.have.property("playAt");
      expect(message.playAt).to.be.above(nowPlus3SecLoBound);
      expect(message.playAt).to.be.below(nowPlus3SecHiBound);
    });
  });

  it("starts movie at correct time when receiving 'play' message", () => {
    const now = Date.now();
    const movieTime = "2:15:34";
    const playAtTime = now + seconds(4);

    // Some user clicked play, and a 'play' message was sent on the queue
    cy.task("mqttSend", {
      type: "play",
      movieTime: movieTime,
      playAt: playAtTime,
    });

    /*****************************************/
    /* Toni's entangled receives the message */
    /*****************************************/

    // Entangled seeks the movie to the 'movieTime'
    cy.getLastCallToMockPlexApi().then((lastMockCall) => {
      // Here '2 15 34' correspond to movieTime: '2:15:34'
      expect(lastMockCall).to.be.equal("seek_to 2 15 34");
    });

    // Then nothing happens until during 'playAt' time, which is 4 sec from now.
    // This allows:
    //  - Time for all players to receive the message
    //  - Time for buffering after they received the msg and
    //    seeked to the correct point in the movie
    cy.get("#e2e-mock-plex-api-calls").contains("play").should("not.exist");

    // When the movie eventually starts, it is exactly 'playAtTime' (+/- delta)
    cy.get("#e2e-mock-plex-api-calls")
      .contains("play")
      .then((_) => {
        const timeWhenMovieStartsPlaying = Date.now();
        expect(timeWhenMovieStartsPlaying).is.closeTo(playAtTime, deltaMs);
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
