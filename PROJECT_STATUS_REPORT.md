# Entangled - Project Status Report

## What Is This?

Entangled is a **synchronized movie-watching app** for Plex. When you and a friend each have Plex running, Entangled keeps your playback in sync — one person clicks Play, and both players start at the same position at the same moment. It also supports synchronized Pause and Resume.

**Architecture:**
```
You (Browser) ──→ Your Flask Server ──→ MQTT Broker ──→ Friend's Flask Server ──→ Friend's Plex
                        ↓                                        ↓
                   Your Plex                                Friend's Plex
```

Each person runs a local Flask web app (port 7777) connected to their Plex player. An MQTT message broker relays commands between the two instances. When you click "Play", the system reads your current movie position, calculates a future timestamp (now + 30 seconds), and broadcasts that over MQTT. Both sides then seek to the same position and schedule `play()` to fire at the exact same wall-clock moment.

---

## What's Done (and working well)

The core product is **feature-complete**. The last commit was July 2025, and all the fundamental pieces are in place:

| Feature | Status | Notes |
|---|---|---|
| Play synchronization | **Done** | Seeks + schedules simultaneous play |
| Pause synchronization | **Done** | Added in the most recent commit |
| Resume synchronization | **Done** | Added in the most recent commit |
| MQTT messaging | **Done** | Pub/sub with SSL/TLS support |
| Plex API integration | **Done** | Connect, seek, play, pause, get timeline |
| Web UI | **Done** | Clean page with Play/Pause/Resume buttons |
| Precision scheduler | **Done** | Thread-based, millisecond-accurate timing |
| Unit tests | **Done** | 32 tests, all passing |
| E2E test infrastructure | **Done** | Cypress + mock Plex API |
| MQTT Docker broker | **Done** | `eclipse-mosquitto` with auth |

The codebase is small (~670 lines of Python) and cleanly structured. The test suite covers all the important message flows. This is solid work.

---

## What's Left To Do

Here's what stands between the current state and actually watching a movie with your friend, ordered from **most critical** to **nice-to-have**:

### 1. MQTT Broker: Hardcoded to your old server (BLOCKING)

**The problem:** `config.py:18` hardcodes the MQTT broker to `floriankempenich.com:6789`. This was presumably your personal server. If that server is no longer running (likely, given the gap), nothing works at all — messages have nowhere to go.

**What to do:** You need a working MQTT broker that both you and your friend can reach. Options:
- **Self-host (easiest):** One of you runs the Docker broker that's already set up in `mqtt/`. Just run `./mqtt/start_mqtt.sh <password>` and point the config at that machine's IP. You'd need to either be on the same network, or set up port forwarding / a VPN.
- **Make the broker address configurable:** Right now the domain/port are hardcoded in `config.py`. These should come from environment variables so each deployment can point at the right broker.

**Effort:** ~1-2 hours to make config flexible + set up broker.

---

### 2. No `.env` example file (BLOCKING for setup)

**The problem:** The app requires 5 environment variables (`MQTT_USER`, `MQTT_PASS`, `PLEX_USER`, `PLEX_PASS`, `PLEX_RESOURCE`) but there's no `.env.example` to tell a user what's needed. Your friend will have no idea what to configure.

**What to do:** Create `entangled/.env.example` with all required variables documented.

**Effort:** 15 minutes.

---

### 3. Both users receive their own commands (DESIGN ISSUE)

**The problem:** When User A clicks Play, the MQTT message is published to the `entangled` topic. But User A is *also* subscribed to that topic, so they receive their own command back. This means User A's Plex will be *seek*-ed and *play*-scheduled just like User B's — even though User A was already at the right position and playing. This could cause a visible glitch (a brief seek + pause + play restart) on the sender's side.

**What to do:** Either:
- Add a `sender_id` field to messages and ignore your own messages, or
- Use two separate MQTT topics (one per direction), or
- Accept the minor glitch if it doesn't bother you in practice (the 30-second delay means it's re-syncing both sides, which might actually be the intended behavior for robustness)

**Effort:** ~1-2 hours for the sender_id approach.

---

### 4. No MQTT reconnection logic (RELIABILITY)

**The problem:** `mqtt.py` connects once and never reconnects. If the network hiccups during a 2-hour movie, the MQTT connection drops silently and no further commands will work. There's no error handling, no retry, and no indication to the user that something is wrong.

**What to do:** Add `on_disconnect` callback with automatic reconnection and exponential backoff. `paho-mqtt` supports `reconnect_delay_set()` for this.

**Effort:** ~2-3 hours.

---

### 5. No feedback when things go wrong (USABILITY)

**The problem:** The web UI always shows a brief "Synchronizing playback..." message regardless of whether it actually worked. If Plex isn't connected, if MQTT is down, if credentials are wrong — the user sees the same optimistic message. Debugging requires reading Flask logs in the terminal.

**What to do:**
- Return actual error status from the Flask endpoints (currently they always return `'playing'` / `'pausing'` etc.)
- Show connection status on the web UI (MQTT connected? Plex connected?)
- Show errors in the UI when something fails

**Effort:** ~4-6 hours.

---

### 6. No deployment guide for two remote friends (USABILITY)

**The problem:** There's no documentation for the real-world scenario: two people on different home networks trying to use this. Questions like "how do I expose my MQTT broker to the internet?" or "do I need port forwarding?" are unanswered.

**What to do:** Write a setup guide covering:
- How to run the MQTT broker
- How to configure port forwarding or use a VPN (e.g., Tailscale)
- How each person sets up their `.env` and starts the app
- How to find your `PLEX_RESOURCE` name (there's a script `print_all_resources.py` but it's not documented)

**Effort:** ~2-3 hours.

---

### 7. One skipped E2E test (MINOR)

**The problem:** The "sends 'play' message when clicking 'Play'" E2E test is skipped because scheduled callbacks from one test bleed into the next. The TODO in `entangled.spec.js:24` explains the issue.

**What to do:** Cancel any pending `RunAtTime` threads between tests, or use a test-scoped scheduler that can be torn down.

**Effort:** ~1-2 hours.

---

### 8. Plex credentials stored as plaintext password (MINOR)

**The problem:** `plex.py:95` uses `PLEX_PASS` with `MyPlexAccount(username, password)`. Plex supports authentication tokens which are more secure and don't require storing your password in plain text.

**What to do:** Switch to token-based auth: log in once, save the token, use `MyPlexAccount(token=...)` going forward.

**Effort:** ~1 hour.

---

### 9. `client-id` collision if two people use default config (MINOR)

**The problem:** `config.py:21` hardcodes `'client-id': 'entangled-florian'`. MQTT requires unique client IDs per connection. If both you and your friend use the default config, MQTT will keep disconnecting one of you.

**What to do:** Generate a unique client ID per instance (e.g., `f'entangled-{uuid4().hex[:8]}'`) or make it configurable.

**Effort:** 10 minutes.

---

## Minimum Viable Movie Night

If you want the shortest path to actually watching a movie together, here's what I'd prioritize:

1. **Fix the MQTT broker situation** — make domain/port/client-id configurable via env vars
2. **Create a `.env.example`** — so your friend knows what to fill in
3. **Set up the MQTT broker** — one of you runs the Docker broker, or use a cloud broker
4. **Fix the client-id collision** — otherwise two instances will fight
5. **Test end-to-end with a real Plex setup** — verify the whole flow works

Items 1, 2, and 4 are probably **~2 hours of code changes**. Item 3 is infrastructure setup. Item 5 is manual testing.

The reconnection logic (#4), error feedback (#5), and deployment guide (#6) would make the experience much more robust, but you could get away without them for a single movie night if the network is stable.

---

## Summary

You were very close. The core synchronization logic is complete and well-tested. What stopped you was the last-mile operational stuff: making the configuration flexible enough for two real people to run it, and making sure it's resilient enough to survive a 2-hour movie session. A focused weekend of work would get this across the finish line.
