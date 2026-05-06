# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

A fully Dockerized stack for running a **BitcoinPurple (BTCP)** full node, an **ElectrumX** server, and a **web dashboard**. All three services communicate over a shared Docker network named `purple`.

## Common Commands

```bash
# First-time setup — copy and fill in credentials before starting
cp .env.example .env
# edit .env: set RPC_USER, RPC_PASSWORD, and any other variables

# Start all services (first run builds images — takes 5–10 min)
docker compose up -d

# Rebuild after code changes
docker compose up -d --build

# Tail logs
docker compose logs -f                   # all services
docker compose logs -f dashboard         # dashboard only

# Run unit tests (offline, no Docker needed)
pip install -r test/requirements.txt
pytest test/unit/ -v

# Run a single test file or test function
pytest test/unit/test_auth.py -v
pytest test/unit/test_auth.py::test_trusted_ip_loopback -v

# Run integration tests (requires docker compose up -d)
pytest test/integration/ -v

# Run e2e tests (auto builds and starts the stack)
pytest test/e2e/ -v --timeout=180

# Generate a secure API key for external access
./generate-api-key.sh

# Download or re-download node binaries
cd daemon && ./download-binaries.sh
cd daemon && ./download-binaries.sh --platform linux --arch aarch64   # Raspberry Pi

# Query the node directly (credentials are in the runtime conf — no flags needed)
docker exec bitcoinpurple-node bitcoinpurple-cli getblockchaininfo
```

## Architecture

```
Internet              Docker Host (purple network)
   ├─ P2P  :13496 ──► bitcoinpurpled   ← blockchain data in .bitcoinpurple/
   ├─ TCP  :50001 ──► electrumx        ← index in electrumx-data/
   ├─ SSL  :50002 ──► electrumx        ← certs auto-generated in certs/
   └─ HTTP :8080  ──► dashboard (Flask) ← reads node + electrumx via internal RPC
```

- **RPC and ZMQ ports are not exposed on the host** — only reachable inside `purple`.
- External stacks join `purple` with `external: true` and connect via Docker hostnames (`bitcoinpurpled:13495`, `electrumx:8000`, etc.).

## Key Files

- [docker-compose.yml](docker-compose.yml) — service definitions, port bindings, env vars
- [Dockerfile.node](Dockerfile.node) / [Dockerfile.electrumx](Dockerfile.electrumx) / [Dockerfile.dashboard](Dockerfile.dashboard) — per-service images
- [entrypoint.sh](entrypoint.sh) — ElectrumX startup: reads RPC creds from env, auto-generates SSL certs, detects public IP, patches `coins.py` TX stats from live node
- [node-entrypoint.sh](node-entrypoint.sh) — node startup: generates `bitcoinpurple.conf` from `.example` on first run, injects `RPC_USER`/`RPC_PASSWORD` from env, then execs `bitcoinpurpled`
- [electrumx-patch/coins_btcp.py](electrumx-patch/coins_btcp.py) — BitcoinPurple coin definition injected into ElectrumX; contains chain params sourced from `src/kernel/chainparams.cpp`
- [web-dashboard/app.py](web-dashboard/app.py) — Flask backend; proxies RPC calls to node and ElectrumX, serves REST API and HTML pages
- [.bitcoinpurple/bitcoinpurple.conf.example](.bitcoinpurple/bitcoinpurple.conf.example) — template for the node config (no credentials); `bitcoinpurple.conf` is generated at container startup and gitignored
- [daemon/download-binaries.sh](daemon/download-binaries.sh) — downloads pre-compiled node binaries from GitHub releases
- [doc/](doc/) — supplementary documentation: `configuration.md`, `networking.md`, `security.md`, `troubleshooting.md`, `technical-data.md`

## Dashboard Authentication Model

| Client origin | Dashboard pages | API (`/api/*`) |
|---|---|---|
| Localhost / LAN (RFC1918) | No auth | No auth |
| External IP | HTTP Basic Auth | `X-API-Key` or `Authorization: Bearer` header |

External access is configured via `.env` (copy `.env.example`). Variables: `DASHBOARD_AUTH_USERNAME`, `DASHBOARD_AUTH_PASSWORD`, `API_KEY`, `DASHBOARD_SESSION_HOURS`, `DASHBOARD_SESSION_COOKIE_SECURE`.

Auth uses `hmac.compare_digest` for constant-time credential validation. `is_trusted_client_ip()` handles both IPv4 RFC1918 ranges and IPv6-mapped IPv4. X-Forwarded-For is intentionally ignored — only `request.remote_addr` is trusted.

## Dashboard Caching

`app.py` uses a two-tier in-memory cache for ElectrumX stats:

- **Fast tier** (60 s) — server version, protocol, basic stats
- **Heavy tier** (120 s) — full peer discovery + genesis-hash verification against all addnodes in `bitcoinpurple.conf`

An empty peer list triggers a faster 15 s refresh. Cache entries are always returned as deep copies to prevent mutation. `warm_electrumx_caches_async()` pre-warms both tiers on Flask startup.

## ElectrumX Coin Definition

`electrumx-patch/coins_btcp.py` defines `BitcoinPurple(Bitcoin)` and `BitcoinPurpleTestnet`. When modifying chain params, cross-reference `src/kernel/chainparams.cpp` in the bitcoinpurplecore repo. `TX_COUNT` and `TX_COUNT_HEIGHT` are patched at container startup via `getchaintxstats` RPC — the values in the file are only defaults used if the node is unreachable.

## entrypoint.sh Startup Sequence

The ElectrumX container startup runs these steps in order before exec-ing `electrumx_server`:

1. Resolve RPC credentials: `RPC_USER`/`RPC_PASSWORD` env vars take priority; falls back to `rpcuser`/`rpcpassword` in the mounted `bitcoinpurple.conf` (written there by `node-entrypoint.sh`)
2. Build `DAEMON_URL=http://user:pass@bitcoinpurpled:rpcport/`
3. Detect public IP (tries icanhazip.com → ifconfig.me → api.ipify.org) and export `REPORT_SERVICES`
4. Inject bootstrap peers from `ELECTRUMX_PEERS` env var into `coins.py`
5. Generate a 4096-bit self-signed SSL certificate (SAN includes public IP) if not already present
6. Patch `TX_COUNT` / `TX_COUNT_HEIGHT` via `getchaintxstats` RPC

## Testing

Tests are organized in three layers under `test/`:

| Layer | Path | Dependencies |
|---|---|---|
| Unit | `test/unit/` | None (mocked) |
| Integration | `test/integration/` | `docker compose up -d` |
| E2E | `test/e2e/` | Auto-builds stack |

`test/conftest.py` provides a session-scoped `flask_app` fixture and a function-scoped `client` fixture. `test/fixtures.py` provides `MOCK_RPC_DATA` (10 RPC methods), `MOCK_ELECTRUMX_STATS`, `local_env()` (REMOTE_ADDR=127.0.0.1), and `external_env(**headers)` (REMOTE_ADDR=8.8.8.8) — use these helpers in new unit tests instead of building environ dicts by hand.

## Testnet

1. Add `testnet=1` and `rpcport=23495` to `.bitcoinpurple/bitcoinpurple.conf.example` (the conf is regenerated from this template at each container startup)
2. Set `NET: "testnet"` in the `electrumx` service in `docker-compose.yml`
3. Clear ElectrumX index: `rm -rf ./electrumx-data/*`
4. Restart: `docker compose up -d`
