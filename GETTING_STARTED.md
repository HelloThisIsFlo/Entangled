# Entangled - Getting Started Guide

Entangled lets you and a friend watch the same movie on Plex, perfectly synchronized.
When one person clicks Play, Pause, or Resume, it happens on **both** screens at the same time.

**How it works:** Each person runs the Entangled app locally. It connects to a shared MQTT broker. When you press Play, a message is sent with the current movie time and a future timestamp. Both apps receive the message, seek to the right position, and start playback at the exact same moment.

---

## Prerequisites

| Tool | How to install | Verify |
|------|---------------|--------|
| **uv** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `uv --version` |
| **Docker** | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) | `docker --version` |
| **Docker Compose** | Comes with Docker Desktop, or install separately | `docker compose version` |
| **Plex account** | [plex.tv](https://plex.tv) | You can log in |
| **Plex client** | A device running a Plex player (TV, computer, etc.) | Playing a movie works |

---

## Step 1: Install dependencies

```bash
git clone <this-repo> && cd Entangled
make install
```

> **Verify:** Run the tests to confirm everything is set up correctly:
> ```bash
> make test
> ```
> **Expected:** `32 passed` with no errors.
>
> Note: The tests use mock MQTT credentials, so you don't need a broker running yet.

---

## Step 2: Deploy the MQTT broker

The MQTT broker is the central message relay. Both you and your friend connect to it.
Pick **one** of the three options below.

### Option A: Local Docker (same network / quick test)

Use this if you and your friend are on the same local network, or just to test things out.

**2A.1 — Set the MQTT password:**
```bash
make mqtt-password
```
Enter a password when prompted. Remember it — you'll need it in Step 3.

> **Verify:** The password file was created:
> ```bash
> cat mqtt/config/password
> ```
> **Expected:** A single line with `entangled:` followed by a hashed password (not plaintext).

**2A.2 — Start the broker:**
```bash
make mqtt-local
```

> **Verify:** The broker is running:
> ```bash
> docker ps | grep entangled-mqtt
> ```
> **Expected:** A running container named `entangled-mqtt`.

> **Verify:** You can connect to it (install mosquitto-clients if needed):
> ```bash
> # In terminal 1 — subscribe:
> mosquitto_sub -h localhost -p 1883 -t "test" -u entangled -P <your-password>
>
> # In terminal 2 — publish:
> mosquitto_pub -h localhost -p 1883 -t "test" -m "hello" -u entangled -P <your-password>
> ```
> **Expected:** Terminal 1 prints `hello`.

**When using this option**, set these values in your `.env` (Step 3):
```
MQTT_DOMAIN=localhost
MQTT_PORT=1883
MQTT_USE_SSL=false
```

---

### Option B: Local Docker + Cloudflare Tunnel (remote friends)

Use this to run the MQTT broker on your machine but make it accessible to your friend over the internet via Cloudflare Tunnel. The domain will be `themac-entangled.kempenich.dev`.

**2B.1 — Create the Cloudflare Tunnel:**

1. Go to [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/) → Networks → Tunnels
2. Click **Create a tunnel**
3. Name it `themac-entangled`
4. Choose **Cloudflared** as the connector
5. Copy the **tunnel token** (a long string starting with `ey...`)
6. Add a **public hostname**:
   - Subdomain: `themac-entangled`
   - Domain: `kempenich.dev`
   - Service Type: `TCP`
   - URL: `mosquitto:1883`

**2B.2 — Set the MQTT password** (if not done already):
```bash
make mqtt-password
```

**2B.3 — Start the broker + tunnel:**
```bash
export CLOUDFLARE_TUNNEL_TOKEN="<your-tunnel-token>"
make mqtt-tunnel
```

> **Verify:** Both containers are running:
> ```bash
> docker ps | grep entangled
> ```
> **Expected:** Two containers: `entangled-mqtt` and `entangled-tunnel`.

> **Verify:** The tunnel is active in the Cloudflare dashboard (status: HEALTHY).

> **Verify:** Test connectivity from another machine (or after installing `cloudflared` for TCP proxy):
>
> Note: MQTT is a TCP protocol, not HTTP. To connect through a Cloudflare Tunnel you need
> `cloudflared access` on the client side:
> ```bash
> # On the client machine, proxy the tunnel locally:
> cloudflared access tcp --hostname themac-entangled.kempenich.dev --url localhost:1884
>
> # Then test:
> mosquitto_sub -h localhost -p 1884 -t "test" -u entangled -P <your-password>
> ```

**When using this option**, the config for your `.env` depends on who's connecting:
- **You (on the same machine as the broker):** `MQTT_DOMAIN=localhost`, `MQTT_PORT=1883`, `MQTT_USE_SSL=false`
- **Your friend (remote):** They need to run `cloudflared access tcp --hostname themac-entangled.kempenich.dev --url localhost:1884` and use `MQTT_DOMAIN=localhost`, `MQTT_PORT=1884`, `MQTT_USE_SSL=false`

---

### Option C: Kubernetes (production / always-on)

Use this to deploy the broker on your home Kubernetes cluster. The domain will be `thehome-entangled.kempenich.dev`.

**2C.1 — Set the MQTT password** (if not done already):
```bash
make mqtt-password
```

**2C.2 — Create the password secret:**
```bash
# Base64-encode the password file
PASSWORD_B64=$(cat mqtt/config/password | base64 -w 0)

# Update the secret manifest
sed "s|REPLACE_WITH_BASE64_ENCODED_PASSWORD_FILE|${PASSWORD_B64}|" \
    k8s/mosquitto-secret.yaml > /tmp/mosquitto-secret-filled.yaml
```

**2C.3 — Apply the manifests:**
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f /tmp/mosquitto-secret-filled.yaml
kubectl apply -f k8s/mosquitto-configmap.yaml
kubectl apply -f k8s/mosquitto-deployment.yaml
```

> **Verify:** The pod is running:
> ```bash
> kubectl get pods -n entangled
> ```
> **Expected:** `mosquitto-xxxxx` with status `Running`.

> **Verify:** The service is reachable within the cluster:
> ```bash
> kubectl run mqtt-test --rm -it --image=eclipse-mosquitto:2 -n entangled --restart=Never -- \
>   mosquitto_pub -h mosquitto.entangled.svc.cluster.local -p 1883 -t "test" -m "hello" -u entangled -P <your-password>
> ```
> **Expected:** No errors.

**2C.4 — Configure Cloudflare Tunnel:**

Your `cloudflared` daemon on the cluster needs a rule to route `thehome-entangled.kempenich.dev` to the Mosquitto service.

Add this to your cloudflared config (typically a ConfigMap for the `cloudflared` deployment):

```yaml
ingress:
  # ... your existing rules ...
  - hostname: thehome-entangled.kempenich.dev
    service: tcp://mosquitto.entangled.svc.cluster.local:1883
  # ... catch-all rule must be last ...
  - service: http_status:404
```

Then restart the cloudflared pod to pick up the new config.

> **Verify:** From your local machine:
> ```bash
> cloudflared access tcp --hostname thehome-entangled.kempenich.dev --url localhost:1884
>
> # In another terminal:
> mosquitto_sub -h localhost -p 1884 -t "test" -u entangled -P <your-password>
> ```
> **Expected:** Connection succeeds (hangs waiting for messages, no error).

**When using this option**, both you and your friend connect via the tunnel:
```bash
# Each person runs this on their machine:
cloudflared access tcp --hostname thehome-entangled.kempenich.dev --url localhost:1884
```
Then in `.env`: `MQTT_DOMAIN=localhost`, `MQTT_PORT=1884`, `MQTT_USE_SSL=false`

---

## Step 3: Configure Entangled

**3.1 — Create your `.env` file:**
```bash
cp entangled/.env.example entangled/.env
```

**3.2 — Edit `entangled/.env`:**
```bash
# MQTT credentials (must match what you set in Step 2)
MQTT_USER=entangled
MQTT_PASS=<the-password-you-chose>

# Your Plex account
PLEX_USER=<your-plex-email>
PLEX_PASS=<your-plex-password>

# Leave empty for now — we'll fill it in the next step
PLEX_RESOURCE=
```

**3.3 — Update `entangled/entangled/config.py`** with your MQTT broker settings:

The config currently has hardcoded values. Update the `config` dict to match your setup:

```python
config = {
    'mqtt': {
        'user': os.environ['MQTT_USER'],
        'pass': os.environ['MQTT_PASS'],
        'domain': 'localhost',        # Change if using a remote broker
        'port': 1883,                 # Change if using a tunnel (e.g. 1884)
        'topic': 'entangled',
        'client-id': 'entangled-<your-name>',  # Unique per person!
        'use-ssl': False              # False for Docker/tunnel setups
    },
    ...
}
```

> **Important:** Each person must have a **unique `client-id`**! If two clients connect with the same ID, one will get disconnected. Use something like `entangled-florian` and `entangled-toni`.

---

## Step 4: Find your Plex resource

**4.1 — List available resources:**
```bash
make list-plex-resources
```

> **Expected:** A list like:
> ```
> [<MyPlexResource:LivingRoomTV>, <MyPlexResource:MacBook>, ...]
> ```

**4.2 — Update your `.env`:**

Pick the resource you'll be watching on and add its name:
```
PLEX_RESOURCE=LivingRoomTV
```

> **Verify:** Run `make list-plex-resources` again. No errors means your credentials are correct.

---

## Step 5: Start Entangled

```bash
make run
```

> **Verify:** Open [http://localhost:7777](http://localhost:7777) in your browser.
> **Expected:** You see the Entangled page with Play, Pause, and Resume buttons.

> **Verify the debug page:** Open [http://localhost:7777/debug](http://localhost:7777/debug).
> Start a movie on your Plex player, then click "Refresh" next to "Current Movie Time".
> **Expected:** It shows the current timestamp of your movie.

---

## Step 6: Movie Night!

### Checklist for both you and your friend:

- [ ] MQTT broker is running and accessible to both of you (verified in Step 2)
- [ ] Each person has Entangled installed (`make install`) with their own `.env`
- [ ] Each person has a **unique `client-id`** in `config.py`
- [ ] Each person starts the same movie on their Plex player (paused at the beginning)
- [ ] Each person runs `make run`
- [ ] Each person opens [http://localhost:7777](http://localhost:7777)

### To sync:

1. One person clicks **Play** → both players seek to the current position and start at the same time
2. Need a bathroom break? Click **Pause** → both players pause simultaneously
3. Ready to continue? Click **Resume** → both players resume at the same time

The sync accounts for a 30-second delay (configurable in `config.py` under `start_delay`) to allow both players to buffer after seeking.

---

## Troubleshooting

### "Connection refused" when connecting to MQTT
- Is the broker running? `docker ps | grep entangled-mqtt`
- Are you using the right port? (1883 for local, 1884 if proxying through cloudflared)
- Is the password correct? Re-run `make mqtt-password` and update your `.env`

### "No PLEX_RESOURCE specified"
- Run `make list-plex-resources` and set `PLEX_RESOURCE` in your `.env`
- Make sure your Plex player is online and visible to your account

### "Failed to connect to Plex account"
- Check your `PLEX_USER` and `PLEX_PASS` in `.env`
- Make sure you can log into [plex.tv](https://plex.tv) with those credentials

### Playback doesn't start simultaneously
- Both players need to have the movie loaded (paused) before clicking Play
- The 30-second delay in `config.py` gives time for buffering — increase it if your connection is slow
- Make sure both clients have unique `client-id` values

### Tests fail with "ModuleNotFoundError"
- Run `make install` first
- Make sure you're running from the repo root directory
