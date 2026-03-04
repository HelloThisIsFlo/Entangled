.PHONY: install test run list-plex-resources mqtt-local mqtt-local-down mqtt-tunnel mqtt-tunnel-down mqtt-password

## Setup
install:
	uv sync --extra dev

test:
	uv run pytest entangled/entangled/tests/ -v

## Run the app
run:
	cd entangled && FLASK_APP="entangled.server:initialize_app('prod')" uv run --project .. flask run -p 7777 -h 0.0.0.0

## Plex helpers
list-plex-resources:
	cd entangled && uv run --project .. python print_all_resources.py

## MQTT broker
mqtt-password:
	@read -p "Enter MQTT password: " pass && ./mqtt/setup_password.sh $$pass

mqtt-local:
	docker compose -f mqtt/docker-compose.yml up -d

mqtt-local-down:
	docker compose -f mqtt/docker-compose.yml down

mqtt-tunnel:
	@test -n "$(CLOUDFLARE_TUNNEL_TOKEN)" || (echo "Error: Set CLOUDFLARE_TUNNEL_TOKEN env var first" && exit 1)
	CLOUDFLARE_TUNNEL_TOKEN=$(CLOUDFLARE_TUNNEL_TOKEN) docker compose -f mqtt/docker-compose.tunnel.yml up -d

mqtt-tunnel-down:
	docker compose -f mqtt/docker-compose.tunnel.yml down
