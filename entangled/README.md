# Entangled

Synchronized movie watching for Plex.

See [GETTING_STARTED.md](../GETTING_STARTED.md) for the full setup guide.

## Quick Start

```bash
make install       # Install dependencies
make test          # Run tests (32 should pass)
make mqtt-password # Set MQTT broker password
make mqtt-local    # Start local MQTT broker
make run           # Start the app on http://localhost:7777
```

## Environment Variables

Copy `entangled/.env.example` to `entangled/.env` and fill in:

- `MQTT_USER` / `MQTT_PASS` — MQTT broker credentials
- `PLEX_USER` / `PLEX_PASS` — Your Plex account
- `PLEX_RESOURCE` — Your Plex player name (run `make list-plex-resources` to find it)
