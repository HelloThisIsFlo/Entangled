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
| Config system | Hardcoded dict + env vars | Working |
| E2E tests | Cypress (legacy, not upgraded) | Partially implemented |
| Unit tests | pytest | **32/32 passing** |
| Package management | uv + pyproject.toml | **Modernized** |
| MQTT deployment | Docker Compose + Cloudflare Tunnel + K8s | **Ready** |

---

## What's Done (and working well)

1. **Core sync protocol** — The full play/pause/resume flow is implemented and tested:
   - User clicks a button -> app reads current movie time from Plex -> broadcasts an MQTT message with `movieTime` + a future `playAt`/`pauseAt`/`resumeAt` timestamp
   - All receivers seek to the correct position and schedule the command to fire at the exact timestamp

2. **Plex API integration** (`PythonLibPlexApi`) — Fully implemented with:
   - Account/resource connection
   - `current_movie_time()`, `seek_to()`, `play()`, `pause()`
   - Resource discovery (`all_resources()` + `print_all_resources.py` helper)
   - Proper error handling with `PlexConnectionError`

3. **MQTT client** — Working pub/sub with listener pattern, SSL support, clean disconnect on exit, updated to paho-mqtt v2 API

4. **Web UI** — Clean interface with Play/Pause/Resume buttons, plus a testing interface for E2E

5. **Unit tests** — All 32 tests pass (0 warnings), covering send/receive for play/pause/resume, config loading, and mock Plex API

6. **Modern tooling** — `uv sync --extra dev` installs everything, `make test` runs tests, `make run` starts the app

---

## Modernization Completed

| Before | After |
|--------|-------|
| Pipfile + pipenv | `pyproject.toml` + `uv` |
| paho-mqtt v1 callback API (deprecation warnings) | paho-mqtt v2 API (clean) |
| Manual MQTT broker setup script | Docker Compose (local, with tunnel) + K8s manifests |
| No `.env` template | `.env.example` with all required vars |
| No unified entry point | `Makefile` with `install`, `test`, `run`, `mqtt-*` targets |
| Basic README | Comprehensive `GETTING_STARTED.md` with step-by-step validation |

---

## Known Limitations

### 1. Config class is built but not wired up
A `Config` class exists in `config.py` that loads settings from a `~/.entangled` YAML file, and it has tests. However, the app still uses a hardcoded `config` dict with environment variables. This works fine — it just means MQTT domain/port are edited in code rather than a config file.

### 2. E2E test interference issue
There's a known issue noted in `entangled.spec.js` where scheduled callbacks bleed into subsequent tests. The workaround (300-second delay in E2E mode) is functional but fragile. The E2E tests were not upgraded (Cypress 5.3) — the 32 pytest unit tests cover all logic.

### 3. Experiments directory
The `experiments/` directory contains old PoC code (PlexClientApiJS with webpack, Python sandbox scripts). Kept for historical reference.

---

## What's Left: Just Configuration

The core logic is complete and tested. To use Entangled for movie night:

1. **Deploy the MQTT broker** — follow `GETTING_STARTED.md` Step 2
2. **Configure `.env` files** — follow `GETTING_STARTED.md` Step 3
3. **Update MQTT connection settings** in `config.py` (domain, port, client-id)
4. **Run `make run`** on both machines

See `GETTING_STARTED.md` for the full step-by-step guide with validation at each stage.
