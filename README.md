# purple-stack — BitcoinPurple Full Node Stack

A fully Dockerized stack for running a **BitcoinPurple (BTCP)** full node, an **ElectrumX**
server, and a **web dashboard** — all three services start with a single `docker compose up`.

## Overview

| Property | Value |
|----------|-------|
| Coin | BitcoinPurple (BTCP) |
| Network | mainnet (testnet supported) |
| PoW algorithm | SHA-256d |
| Block time | ~1 minute |
| Status | Experimental |

### Services

| Service | Description | Default ports (host-exposed) |
|---------|-------------|------------------------------|
| `bitcoinpurpled` | BitcoinPurple full node | `13496` P2P |
| `electrumx` | ElectrumX Electrum protocol server | `50001` TCP · `50002` SSL |
| `dashboard` | Real-time monitoring UI + REST API | `8080` HTTP |

RPC (13495), ZMQ (28332–28335), and the ElectrumX internal RPC (8000) are **not** exposed
on the host — they are only reachable inside the `purple` Docker network.

---

## What this stack includes

### 1. BitcoinPurple full node

Pre-compiled `bitcoinpurpled` and `bitcoinpurple-cli` binaries downloaded from
[BitcoinPurpleBlockchain/bitcoinpurplecore](https://github.com/BitcoinPurpleBlockchain/bitcoinpurplecore)
and packaged into a minimal Ubuntu 22.04 image (`Dockerfile.node`).

On first start, `node-entrypoint.sh` copies `.bitcoinpurple/bitcoinpurple.conf.example`
to `bitcoinpurple.conf`, then prepends `rpcuser` / `rpcpassword` from the environment.
On subsequent starts it only re-injects the credentials — the rest of the conf is left
as-is. Credentials are never stored in the conf template or in version control.

### 2. ElectrumX server (patched for BTCP)

Based on `lukechilds/electrumx` (upstream: [kyuupichan/electrumx](https://github.com/kyuupichan/electrumx)).
The `BitcoinPurple` and `BitcoinPurpleTestnet` coin classes are injected into
`electrumx/lib/coins.py` at Docker build time from `electrumx-patch/coins_btcp.py`.

A custom `entrypoint.sh` runs before `electrumx_server` and handles:

1. RPC credential resolution (`RPC_USER`/`RPC_PASSWORD` env → `bitcoinpurple.conf` fallback).
2. Automatic `DAEMON_URL` construction.
3. Public IP detection and `REPORT_SERVICES` export for peer announcement.
4. Bootstrap peer injection from `ELECTRUMX_PEERS` into the `BitcoinPurple` coin class.
5. 4096-bit self-signed SSL certificate generation (with public IP in SAN) if none exists.
6. `TX_COUNT` / `TX_COUNT_HEIGHT` patch via live `getchaintxstats` RPC.
7. Uint16 flush-counter overflow guard: if `hist/flush_count` exceeds the threshold
   (default 60 000), runs `electrumx_compact_history` or wipes the index as a fallback.

### 3. Web dashboard

A Flask application (`web-dashboard/app.py`) that proxies RPC calls to both the node and
ElectrumX and exposes a browser UI and a REST API.

**Pages:**

| Page | URL | Description |
|------|-----|-------------|
| Main dashboard | `/` | System resources, node stats, ElectrumX stats, mempool, recent blocks |
| Node console | `/console` | Read-only `bitcoinpurple-cli` terminal with autocomplete |
| Network peers | `/peers` | Full peer list with traffic stats, auto-refreshes every 10 s |
| Electrum servers | `/electrum-servers` | Discovered ElectrumX peers with TCP/SSL reachability |

**REST API** — all endpoints return JSON:

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Overall service health |
| `GET /api/system/resources` | CPU, memory, disk usage |
| `GET /api/bitcoinpurple/info` | Node info: blockchain, network, mining, mempool |
| `GET /api/bitcoinpurple/block-height` | Current block height |
| `GET /api/bitcoinpurple/network-hashrate` | Network hashrate in H/s |
| `GET /api/bitcoinpurple/difficulty` | Current PoW difficulty |
| `GET /api/bitcoinpurple/coinbase-subsidy` | Current block subsidy in BTCP |
| `GET /api/bitcoinpurple/peers` | Peer list with traffic stats |
| `GET /api/bitcoinpurple/blocks/recent` | Last 10 blocks |
| `GET /api/electrumx/stats` | ElectrumX version, uptime, DB size, ports |
| `GET /api/electrumx/servers` | Discovered ElectrumX peers |
| `GET /api/config` | Returns the configured API key (requires auth) |
| `GET /api/cli/methods` | List all methods allowed by `/api/cli` |
| `POST /api/cli` | Execute a read-only `bitcoinpurple-cli` command |

See [`web-dashboard/README.md`](web-dashboard/README.md) for the full API reference.

---

## Differences from upstream ElectrumX

```text
Coin class added : electrumx/lib/coins.py :: BitcoinPurple(Bitcoin)
                                           :: BitcoinPurpleTestnet(BitcoinPurple)

Genesis hash (mainnet) : 000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015
Genesis hash (testnet) : 000002fdc3921c1ad368816fcc587f499698d42b42ab5a5d94ee67882ef9d998

P2PKH version byte     : 0x38  (addresses start with 'P')
P2SH version byte      : 0x37  (addresses start with 'P')
WIF byte               : 0xb7
Bech32 HRP             : btcp  (testnet: tbtcp)
BIP32 xpub             : 0x0488B21E  (mainnet)
BIP32 xprv             : 0x0488ADE4  (mainnet)

SegWit                 : active from block 0 (BIP141/143/147)
Taproot                : ALWAYS_ACTIVE
Deserializer           : DeserializerSegWit

RPC port (mainnet)     : 13495
RPC port (testnet)     : 23495
P2P port (mainnet)     : 13496
Electrum TCP           : 50001  (testnet: 60001)
Electrum SSL           : 50002  (testnet: 60002)

REORG_LIMIT            : 1200  (×10 vs Bitcoin — 1-minute blocks)
MIN_REQUIRED_DAEMON    : 1.1.1
```

No upstream ElectrumX Python sources are modified directly — the patch is applied
inside the Docker image only.

---

## Requirements

- Docker 20.10+
- Docker Compose 2.0+
- 64-bit Linux / macOS / WSL2
- 4 GB+ RAM
- 50 GB+ free disk (blockchain data grows over time)

No Python, LevelDB, or node binary installation needed on the host — everything runs inside Docker.

---

## Installation

```bash
git clone https://github.com/BitcoinPurpleBlockchain/purple-stack.git
cd purple-stack

# Download pre-compiled node binaries
cd daemon && ./download-binaries.sh && cd ..

# Copy and fill in credentials (required before first start)
cp .env.example .env
# edit .env: set RPC_USER and RPC_PASSWORD

# Build images and start all services
docker compose up -d
```

The first run builds the images (5–10 min) and starts syncing the blockchain — full sync
can take hours to days depending on hardware and bandwidth.

Dashboard: `http://localhost:8080`

---

## Configuration

All configuration lives in `.env`. Copy `.env.example` and edit it before the first start:

```bash
cp .env.example .env
```

```env
# ── Credentials — required, shared by node, ElectrumX, and dashboard ─────────
# Do NOT set rpcuser/rpcpassword in bitcoinpurple.conf — use only these.
RPC_USER=your_username
RPC_PASSWORD=your_strong_password

# ── Ports (defaults shown) ────────────────────────────────────────────────────
ELECTRUMX_TCP_PORT=50001
ELECTRUMX_SSL_PORT=50002
DASHBOARD_PORT=8080

# ── Dashboard auth (required for external / internet-facing access) ───────────
DASHBOARD_AUTH_USERNAME=admin
DASHBOARD_AUTH_PASSWORD=change-me-now
API_KEY=change-me-to-a-long-random-api-key   # generate with ./generate-api-key.sh
DASHBOARD_SESSION_HOURS=1
DASHBOARD_SESSION_COOKIE_SECURE=false        # set true when behind HTTPS

# ── ElectrumX optional ────────────────────────────────────────────────────────
# ELECTRUMX_PEERS=1.2.3.4 t,5.6.7.8 t       # bootstrap peer list

# REPORT_SERVICES is auto-detected at startup (public IP via icanhazip.com / ifconfig.me).
# Override only if the detected IP is wrong: VPN, reverse proxy, or fixed DNS hostname.
# To override: uncomment the line below in docker-compose.yml (NOT in .env):
#   REPORT_SERVICES: "tcp://your.ip:50001,ssl://your.ip:50002"
```

Everything else (`DAEMON_URL`, `COIN`, `NET`, `SERVICES`, SSL paths) is set automatically
at container startup — do not override unless you know what you are doing.

### Node conf

`node-entrypoint.sh` copies `bitcoinpurple.conf.example` → `bitcoinpurple.conf` on first
start only, then injects `RPC_USER` / `RPC_PASSWORD` from `.env`. The key fixed settings:

```ini
txindex=1       # mandatory for ElectrumX — incompatible with prune
server=1
rpcport=13495
zmqpubrawblock=tcp://0.0.0.0:28332
zmqpubrawtx=tcp://0.0.0.0:28333
zmqpubhashblock=tcp://0.0.0.0:28334
zmqpubhashtx=tcp://0.0.0.0:28335
```

Do **not** enable `prune` — it is incompatible with `txindex=1`.

### SSL certificates

Auto-generated on first start and stored in `./certs/`. To use your own certificate,
place `server.crt` and `server.key` in `./certs/` before starting the stack.

---

## Common Commands

```bash
# Start / stop
docker compose up -d
docker compose down

# Rebuild after code changes
docker compose up -d --build

# Tail logs
docker compose logs -f                    # all services
docker compose logs -f electrumx
docker compose logs -f bitcoinpurpled
docker compose logs -f dashboard

# Query the node directly
docker exec bitcoinpurple-node bitcoinpurple-cli getblockchaininfo

# Generate a secure API key for external dashboard access
./generate-api-key.sh
```

---

## Verifying

Check that the node is reachable:

```bash
docker exec bitcoinpurple-node bitcoinpurple-cli getblockchaininfo
```

Check ElectrumX via TCP:

```bash
echo '{"id":0,"method":"server.version","params":["test","1.4"]}' | nc 127.0.0.1 50001
```

Check ElectrumX via its internal RPC:

```bash
docker exec btcp-electrumx electrumx_rpc getinfo
```

Check dashboard health:

```bash
curl http://localhost:8080/api/health | jq
```

---

## Wallet Compatibility

| Wallet | Repository | Protocol |
|--------|-----------|----------|
| Purple Electrum | [BitcoinPurpleBlockchain/purple-electrum](https://github.com/BitcoinPurpleBlockchain/purple-electrum.git) | Electrum 1.4 |

Connect to `127.0.0.1:50001` (TCP) or `127.0.0.1:50002` (SSL) for local use,
or to your server's public IP for remote access.

---

## Port Reference

| Service | Protocol | Port | Exposed on host |
|---------|----------|------|-----------------|
| BitcoinPurple P2P | TCP | 13496 | Yes |
| BitcoinPurple RPC | TCP | 13495 | No (internal only) |
| BitcoinPurple ZMQ | TCP | 28332–28335 | No (internal only) |
| ElectrumX TCP | TCP | 50001 | Yes |
| ElectrumX SSL | TCP | 50002 | Yes |
| ElectrumX internal RPC | TCP | 8000 | No (internal only) |
| Dashboard | HTTP | 8080 | Yes |

Testnet ports: P2P `23496`, RPC `23495`, Electrum TCP `60001`, SSL `60002`.

---

## Testnet

1. Edit `.bitcoinpurple/bitcoinpurple.conf.example`: add `testnet=1` and `rpcport=23495`.
2. Delete the generated conf so it is regenerated from the updated example on next start:
   ```bash
   rm .bitcoinpurple/bitcoinpurple.conf
   ```
3. In `docker-compose.yml`, set `NET: "testnet"` in the `electrumx` service.
4. Wipe the ElectrumX index: `rm -rf ./electrumx-data/*`
5. Restart: `docker compose up -d`

---

## Troubleshooting

**`daemon is not caught up`**
The node has not finished syncing. ElectrumX retries automatically — monitor
`docker compose logs -f bitcoinpurpled`.

**`genesis block has hash … expected …`**
The `NET` variable does not match the running chain. Verify that `NET=mainnet` in
`docker-compose.yml` and that there is no `testnet=1` in the node conf.

**`DB version mismatch` / corrupted index**
Wipe the ElectrumX index and let it resync:
```bash
docker compose stop electrumx
rm -rf ./electrumx-data/*
docker compose up -d electrumx
```

**`struct.error` crash-loop on flush**
The history flush counter hit the uint16 limit (65535). The entrypoint guard handles
this automatically. If it recurs, add `FLUSH_COMPACT_THRESHOLD=50000` to the `electrumx`
environment block in `docker-compose.yml` to trigger compaction earlier.

**Node RPC returns 401**
`RPC_USER` / `RPC_PASSWORD` in `.env` do not match what was written to `bitcoinpurple.conf`
at startup. Stop the stack, verify `.env`, then restart.

**Dashboard shows "node unreachable"**
The node is still starting or syncing. Check `docker compose logs -f bitcoinpurpled`.

**Wallet connection fails**
Check in order:
- Firewall: ports 50001 / 50002 open?
- SSL: self-signed cert must be accepted by the wallet (or replace with a CA-signed cert).
- `ELECTRUMX_TCP_PORT` / `ELECTRUMX_SSL_PORT` in `.env` match the ports you are connecting to.
- `docker compose logs -f electrumx` for handshake errors.

---

## Security

- RPC (13495) and ZMQ (28332–28335) are never exposed on the host.
- External stacks on the same host can reach internal ports by joining the `purple`
  Docker network with `external: true`.
- Change `DASHBOARD_AUTH_PASSWORD` and `API_KEY` before exposing port 8080 to the internet.
- The ElectrumX SSL certificate is self-signed by default — replace it with a CA-signed cert
  for public-facing servers.
- Keep `RPC_USER` / `RPC_PASSWORD` out of version control — `.env` is gitignored.
- Use a reverse proxy with valid TLS for the dashboard in production.

See [`doc/security.md`](doc/security.md) for the full authentication model.

---

## Developer Notes

### Key files

| File | Purpose |
|------|---------|
| `electrumx-patch/coins_btcp.py` | `BitcoinPurple` and `BitcoinPurpleTestnet` coin class definitions |
| `Dockerfile.electrumx` | Patches `coins_btcp.py` into `electrumx/lib/coins.py` at build time |
| `entrypoint.sh` | ElectrumX startup: credentials, IP detection, peers, SSL, TX stats, flush guard |
| `Dockerfile.node` | Downloads node binaries, packages them into Ubuntu 22.04 |
| `node-entrypoint.sh` | Node startup: generates `bitcoinpurple.conf` from template, injects credentials |
| `Dockerfile.dashboard` | Flask dashboard image |
| `web-dashboard/app.py` | Flask backend: RPC proxy, REST API, auth, two-tier caching |
| `docker-compose.yml` | Service definitions, port bindings, shared `purple` network |
| `.bitcoinpurple/bitcoinpurple.conf.example` | Node conf template (no credentials) |

### Running tests

```bash
# Unit tests — offline, no Docker needed
pip install -r test/requirements.txt
pytest test/unit/ -v

# Integration tests — requires docker compose up -d
pytest test/integration/ -v

# End-to-end tests — auto-builds and starts the stack
pytest test/e2e/ -v --timeout=180
```

---

## Documentation

| Doc | Contents |
|-----|----------|
| [`doc/configuration.md`](doc/configuration.md) | Environment variables, ports, node config, testnet, backup |
| [`doc/networking.md`](doc/networking.md) | Architecture, internal endpoints, port forwarding, external stacks |
| [`doc/security.md`](doc/security.md) | Auth model, SSL certificates, firewall |
| [`doc/troubleshooting.md`](doc/troubleshooting.md) | Common issues and fixes |
| [`web-dashboard/README.md`](web-dashboard/README.md) | Dashboard pages, console, full REST API reference |
| [`doc/technical-data.md`](doc/technical-data.md) | Full BTCP chain parameters reference |
| [`test/README.md`](test/README.md) | Test suite: unit, integration, e2e |

---

## License

MIT — see [LICENSE](LICENSE).

ElectrumX is licensed under the MIT License by Neil Hoffman / the ElectrumX contributors.

---

## Credits

- Node: [BitcoinPurpleBlockchain/bitcoinpurplecore](https://github.com/BitcoinPurpleBlockchain/bitcoinpurplecore)
- ElectrumX: [kyuupichan/electrumx](https://github.com/kyuupichan/electrumx) via [lukechilds/electrumx](https://github.com/lukechilds/electrumx)
- Wallet: [BitcoinPurpleBlockchain/purple-electrum](https://github.com/BitcoinPurpleBlockchain/purple-electrum)

Stack and BTCP coin patch by [Davide Grilli](https://github.com/BitcoinPurpleBlockchain).
