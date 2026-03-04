# Entangled - Project Status Report

## What is Entangled?

Entangled is a **synchronized movie-watching app** for Plex. It lets two (or more) people watch the same movie on their own Plex players, perfectly synchronized — when one person presses Play, Pause, or Resume, it happens on everyone's screen at the same time.

It works by coordinating through an **MQTT message broker**: one person's action gets broadcast as a message, and all connected clients receive it and schedule the Plex command to execute at the same future timestamp, compensating for network delay.

---

## Architecture Overview

| Component | Technology | Status |
|---|---|---|
| Backend / Web server | Python + Flask | Implemented |
| Plex integration | `plexapi` Python library | Implemented |
| Message broker | MQTT (Mosquitto via Docker) | Implemented |
| Frontend | Plain HTML/JS | Implemented |
| Scheduling engine | Custom threaded scheduler | Implemented |
| Config system | YAML file-based (`Config` class) | Partially implemented |
| E2E tests | Cypress | Partially implemented |
| Unit tests | pytest | **32/32 passing** |

---

## What's Done (and working well)

1. **Core sync protocol** — The full play/pause/resume flow is implemented and tested:
   - User clicks a button → app reads current movie time from Plex → broadcasts an MQTT message with `movieTime` + a future `playAt`/`pauseAt`/`resumeAt` timestamp
   - All receivers seek to the correct position and schedule the command to fire at the exact timestamp

2. **Plex API integration** (`PythonLibPlexApi`) — Fully implemented with:
   - Account/resource connection
   - `current_movie_time()`, `seek_to()`, `play()`, `pause()`
   - Resource discovery (`all_resources()` + `print_all_resources.py` helper)
   - Proper error handling with `PlexConnectionError`

3. **MQTT client** — Working pub/sub with listener pattern, SSL support, and clean disconnect on exit

4. **Web UI** — Clean interface with Play/Pause/Resume buttons, plus a testing interface for E2E

5. **Unit tests** — All 32 tests pass, covering send/receive for play/pause/resume, config loading, and mock Plex API

6. **Startup scripts** — `start_for_prod.sh` and `start_for_e2e.sh` to launch the Flask server

---

## What's Left To Do

### 1. Config class is not wired up (Medium priority)

A `Config` class exists in `config.py` (lines 30-43) that loads settings from a `~/.entangled` YAML file, and it has tests. However, **the app still uses a hardcoded `config` dict** (lines 14-27) with environment variables for MQTT credentials. The `Config` class was never integrated into the rest of the app.

**What needs to happen:** Replace the hardcoded `config` dict with the `Config` class, and create a sample `~/.entangled` config file template.

### 2. No `.env` file exists (Required for startup)

The README says to create a `.env` file with `MQTT_USER`, `MQTT_PASS`, `PLEX_USER`, `PLEX_PASS`, and `PLEX_RESOURCE`. No `.env` file or `.env.example` template exists in the repo. The `conftest.py` does load from `.env` for tests, but the prod startup scripts don't — they rely on the environment variables being set externally.

**What needs to happen:** Either create a `.env.example` template so you remember which vars to set, or wire up `.env` loading in the prod startup script.

### 3. MQTT broker setup needs your server (Infrastructure)

The hardcoded config points to `floriankempenich.com:6789` with SSL. The `mqtt/` directory has a Docker-based Mosquitto setup script, but it's for local dev. You'll need to either:
- Have your MQTT broker running on your server, or
- Use a cloud MQTT service, or
- Both you and your friend run against the same broker (could be local with port forwarding)

### 4. paho-mqtt deprecation warning (Low priority)

The MQTT client uses the v1 callback API (`mqtt.Client(client_id=...)`) which is deprecated in `paho-mqtt` 2.x. This produces warnings but still works. Eventually the `MQTTClient.__init__` should be updated to use the v2 API.

### 5. E2E test interference issue (Known bug, noted in code)

There's a comment in `entangled.spec.js` (line 24):
> *"The problem was that it would schedule a callback and fuck up the next test. Find a way to prevent that."*

The workaround is using a 300-second delay in E2E mode so scheduled callbacks don't fire during tests. This works but is fragile.

### 6. Both users need the app running (Deployment)

Right now the app runs as a local Flask server on port 7777. For you and your friend to use it together:
- **Both** of you need to run the Entangled app locally (each controlling your own Plex player)
- **Both** need to be connected to the same MQTT broker
- **Both** need Plex credentials and a resource (player) configured

There's no deployment automation, Docker Compose, or install guide beyond the basic README.

---

## Summary: Steps to Movie Night

Here's the concrete checklist to get from current state to watching a movie with your friend:

1. **Set up an MQTT broker** accessible to both of you (your server at `floriankempenich.com:6789` may already work if it's still running)
2. **Create `.env` files** on both machines with the correct `MQTT_USER`, `MQTT_PASS`, `PLEX_USER`, `PLEX_PASS`, and `PLEX_RESOURCE` values
3. **Wire up the `Config` class** OR just make sure the hardcoded config + env vars match your actual setup
4. **Install dependencies** (`pipenv install`) and run `print_all_resources.py` to find each person's Plex resource name
5. **Start the app** on both machines (`./start_for_prod.sh`)
6. **Both open** `http://localhost:7777`, start the same movie on Plex, and use the web UI to sync play/pause/resume

The core logic is complete and tested. The remaining work is primarily **configuration and infrastructure setup** — there's no missing feature logic blocking you.
