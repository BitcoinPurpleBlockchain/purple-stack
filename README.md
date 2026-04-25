# ElectrumX Server with BitcoinPurple (BTCP) Full Node

Complete Dockerized setup for running an **ElectrumX server** with an integrated **BitcoinPurple (BTCP) full node** and **Web Dashboard** for monitoring.

---

## What You Get

| Component | Description | Ports |
|-----------|-------------|-------|
| **BitcoinPurple Full Node** | Full blockchain node (bitcoinpurpled) | `13496` P2P · `13495` RPC (localhost only) |
| **ElectrumX Server** | Electrum protocol server for wallet connections | `50001` TCP · `50002` SSL |
| **Web Dashboard** | Real-time monitoring UI + REST API | `8080` HTTP |

---

## Requirements

- Docker 20.10+ and Docker Compose 2.0+
- 64-bit system (AMD64 or ARM64)
- 4 GB+ RAM, 50 GB+ free disk space
- BitcoinPurple binaries — see [daemon/README.md](daemon/README.md)

**Tested on:** Debian 12/13, Ubuntu 22.04/24.04, Raspberry Pi OS (ARM64), WSL2

---

## Architecture

```
Internet              Docker Host
   │                       │
   ├─ P2P  :13496 ──────► bitcoinpurpled ◄────────────────────────────────┐
   ├─ TCP  :50001 ──────► electrumx      ◄── bitcoinpurpled (RPC, internal)│  purple
   ├─ SSL  :50002 ──────► electrumx                                        │  (Docker network)
   └─ HTTP :8080  ──────► dashboard      ◄── bitcoinpurpled + electrumx ◄──┘
```

All services share the `purple` Docker network. RPC and ZMQ ports are **not** exposed on the host — internal communication uses Docker hostnames (e.g. `bitcoinpurpled:13495`).

---

## Connecting Other Docker Stacks

If you run another stack on the same host (e.g. a mining pool, an explorer, a custom bot) and need to reach the node or ElectrumX, join the shared `purple` network — no ports need to be exposed on the host.

**In your external `docker-compose.yml`:**

```yaml
networks:
  purple:
    external: true   # already created by this stack

services:
  myapp:
    image: ...
    networks:
      - purple
    environment:
      # Connect via service name — Docker resolves it internally
      RPC_HOST: bitcoinpurpled
      RPC_PORT: "13495"
      ZMQ_RAWBLOCK:  "tcp://bitcoinpurpled:28332"
      ZMQ_RAWTX:     "tcp://bitcoinpurpled:28333"
      ZMQ_HASHBLOCK: "tcp://bitcoinpurpled:28334"
      ZMQ_HASHTX:    "tcp://bitcoinpurpled:28335"
      ELECTRUMX_HOST: electrumx
      ELECTRUMX_PORT: "50001"
```

> **Note:** `purple` is created automatically when you run `docker compose up` on this stack for the first time. Start this stack before starting any dependent stack.

### Exposing a port to the host (optional)

By default, RPC and ZMQ ports are only reachable inside `purple`. If you have an application running **directly on the host** (not in Docker) that needs to connect, you can expose a port in `docker-compose.yml`:

```yaml
ports:
  - "127.0.0.1:13495:13495"   # RPC — localhost only (safe)
  - "127.0.0.1:28332:28332"   # ZMQ rawblock — localhost only
  - "127.0.0.1:28333:28333"   # ZMQ rawtx — localhost only
```

Use `127.0.0.1:` as the bind address to restrict access to the local machine only. Using `0.0.0.0:` would make the port reachable from the network — avoid this for RPC and ZMQ.

### Available internal endpoints

| Service | Hostname | Port | Protocol |
|---------|----------|------|----------|
| BitcoinPurple node RPC | `bitcoinpurpled` | `13495` | HTTP JSON-RPC |
| ZMQ rawblock | `bitcoinpurpled` | `28332` | ZMQ pub |
| ZMQ rawtx | `bitcoinpurpled` | `28333` | ZMQ pub |
| ZMQ hashblock | `bitcoinpurpled` | `28334` | ZMQ pub |
| ZMQ hashtx | `bitcoinpurpled` | `28335` | ZMQ pub |
| ElectrumX TCP | `electrumx` | `50001` | Electrum protocol |
| ElectrumX SSL | `electrumx` | `50002` | Electrum protocol (SSL) |
| Web Dashboard | `dashboard` | `8080` | HTTP |

---

## Quick Start

### Step 1 — Get BitcoinPurple Binaries

Use the helper script:

```bash
cd daemon
./download-binaries.sh
```

This downloads and installs the latest compatible binaries into `daemon/`.
→ See [daemon/README.md](daemon/README.md) for advanced options (`--arch`, `--platform`, `--repo`).

### Step 2 — Set RPC Credentials

Open `.bitcoinpurple/bitcoinpurple.conf` and set strong values:

```conf
rpcuser=your_username      # ← change this
rpcpassword=your_password  # ← use a strong password
```

### Step 3 — (Optional) Enable External Access

Skip this step if you only need local/LAN access.

If you plan to expose the dashboard or API to the internet:

```bash
./generate-api-key.sh   # generates a secure API key
cp .env.example .env
nano .env               # paste the key, set username and password
```

→ See [Security](#security) for what each variable controls.

### Step 4 — Start

```bash
docker compose up -d
```

First build: 5–10 minutes. Follow progress with:

```bash
docker compose logs -f
```

### Step 5 — Open the Dashboard

```
http://localhost:8080           # same machine
http://<your-server-ip>:8080   # from LAN
```

→ See [web-dashboard/README.md](web-dashboard/README.md) for features and REST API reference.

---

## Port Forwarding (Public Access)

To expose the stack to the internet, forward these ports on your router:

| Port | Protocol | Service | Required? |
|------|----------|---------|-----------|
| `13496` | TCP | BitcoinPurple P2P node sync | **Yes** |
| `50001` | TCP | ElectrumX — Electrum wallet connections | Recommended |
| `50002` | TCP | ElectrumX SSL — encrypted wallet connections | Recommended |
| `8080` | TCP | Web Dashboard | Optional — see [Security](#security) |

Set the forwarding destination to your server's local IP (`hostname -I | awk '{print $1}'`).

---

## Testnet

1. In `.bitcoinpurple/bitcoinpurple.conf`: add `testnet=1` and `rpcport=23495`
2. In `docker-compose.yml` (electrumx service): set `NET: "testnet"`
3. Clear ElectrumX database: `rm -rf ./electrumx-data/*`
4. Restart: `docker compose up -d`

---

## Common Commands

```bash
# Start / stop
docker compose up -d
docker compose down
docker compose restart

# Logs
docker compose logs -f                   # all services
docker compose logs -f bitcoinpurpled    # node only
docker compose logs -f electrumx         # ElectrumX only
docker compose logs -f dashboard         # dashboard only

# Status and resource usage
docker compose ps
docker stats

# Rebuild after code changes
docker compose up -d --build

# Query the node directly
docker exec bitcoinpurple-node bitcoinpurple-cli \
  -rpcuser=USER -rpcpassword=PASS getblockchaininfo
```

---

## Troubleshooting

**Containers not starting**
Check logs first: `docker compose logs <service-name>`
Common causes: wrong binary architecture, incorrect RPC credentials, port already in use.

**ElectrumX can't connect to the node**
Verify the node is running and credentials in `bitcoinpurple.conf` are correct:
```bash
docker exec bitcoinpurple-node bitcoinpurple-cli -rpcuser=USER -rpcpassword=PASS getblockchaininfo
```

**Dashboard shows services as "down"**
The node and/or ElectrumX may still be syncing or indexing. Check logs and wait.

**Port already in use**
```bash
sudo lsof -i :<port>    # find what is using the port
```

**Wrong binary architecture**
```bash
uname -m                        # your system: x86_64 or aarch64
file daemon/bitcoinpurpled      # binary must match
# if needed, re-download with the helper script:
./daemon/download-binaries.sh --platform linux --arch x86_64
```

**Dashboard not loading from LAN**
```bash
sudo ufw status           # check firewall
sudo ufw allow 8080/tcp  # open port if needed
netstat -tln | grep 8080  # verify dashboard is listening on 0.0.0.0:8080
```

---

## Security

**Authentication model:**

| Client origin | Dashboard (`/`) | API (`/api/*`) |
|---------------|-----------------|----------------|
| Localhost / LAN (RFC1918) | No auth required | No auth required |
| External / public IP | HTTP Basic Auth | API key required |

Configure in `.env` (copy from `.env.example`):

| Variable | Purpose |
|----------|---------|
| `DASHBOARD_AUTH_USERNAME` | Basic Auth username for external dashboard access |
| `DASHBOARD_AUTH_PASSWORD` | Basic Auth password for external dashboard access |
| `API_KEY` | Key for external API calls (`X-API-Key` header or `Authorization: Bearer`); also signs session cookies |
| `DASHBOARD_SESSION_HOURS` | Session duration after login (hours, default: `1`) |
| `DASHBOARD_SESSION_COOKIE_SECURE` | Set to `true` when serving over HTTPS (default: `false`) |

**Firewall (recommended):**
```bash
sudo ufw allow 13496/tcp   # P2P
sudo ufw allow 50001/tcp   # ElectrumX TCP
sudo ufw allow 50002/tcp   # ElectrumX SSL
# Do NOT open 8080 without configuring auth in .env
sudo ufw enable
```

**SSL certificates:** Auto-generated on first startup in `./certs/` (self-signed, includes the server's public IP in the SAN). Replace with your own certificates (e.g. Let's Encrypt) by placing `server.crt` and `server.key` in `./certs/` before starting.

---

## Project Structure

```
purple-stack/
├── daemon/
│   ├── download-binaries.sh     # Download/extract/install latest BitcoinPurple binaries
│   ├── bitcoinpurpled           # Node daemon binary (downloaded)
│   └── bitcoinpurple-cli        # RPC CLI binary (downloaded)
├── .bitcoinpurple/
│   ├── bitcoinpurple.conf       # Node configuration (edit RPC credentials here)
│   ├── blocks/                  # Blockchain data (auto-generated)
│   └── chainstate/              # Chain state (auto-generated)
├── certs/                       # SSL certificates (auto-generated on first run)
├── electrumx-data/              # ElectrumX database (auto-generated)
├── electrumx-patch/             # BitcoinPurple coin definition for ElectrumX
├── web-dashboard/               # Dashboard source (Flask backend + HTML/JS/CSS)
│   └── README.md                # Dashboard features and API reference
├── docker-compose.yml           # Service orchestration
├── Dockerfile.bitcoinpurple-node
├── Dockerfile.electrumx
├── Dockerfile.dashboard
├── entrypoint.sh                # ElectrumX startup (SSL, IP detection, RPC config)
├── generate-api-key.sh          # Helper to generate a secure API key
├── .env.example                 # Environment variables template
└── test_api.py                  # Dashboard API test suite
```

---

## Backup

- Blockchain: `.bitcoinpurple/blocks/`, `.bitcoinpurple/chainstate/`
- Wallet (if used): `.bitcoinpurple/wallet.dat` — **back this up regularly**
- ElectrumX index: `./electrumx-data/`
- Certificates: `./certs/`

To speed up a fresh install by copying an existing synced blockchain:
```bash
cp -r ~/.bitcoinpurple/blocks .bitcoinpurple/
cp -r ~/.bitcoinpurple/chainstate .bitcoinpurple/
cp -r ~/.bitcoinpurple/indexes .bitcoinpurple/
```

---

## Credits

- **ElectrumX:** [kyuupichan/electrumx](https://github.com/kyuupichan/electrumx)
- **BitcoinPurple Full Node:** [bitcoinpurple/bitcoinpurplecore](https://github.com/bitcoinpurple/bitcoinpurplecore)

Distributed under the **MIT License** — see `LICENSE`.
