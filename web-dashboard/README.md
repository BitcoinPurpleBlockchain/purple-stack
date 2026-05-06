# BitcoinPurple Dashboard — Features & API Reference

Web dashboard for monitoring the BitcoinPurple node and ElectrumX server in real time.

---

## Access

| Context | URL |
|---------|-----|
| Same machine | `http://localhost:8080` |
| LAN | `http://<server-ip>:8080` |
| Internet | `http://<public-ip>:8080` (requires auth — see below) |

To find your server's local IP:
```bash
hostname -I | awk '{print $1}'
```

---

## Pages

| Page | URL | Description |
|------|-----|-------------|
| Main Dashboard | `/` | Tabbed view: system resources, node stats, ElectrumX stats, mempool, recent blocks |
| Node Console | `/console` | Read-only `bitcoinpurple-cli` terminal with autocomplete and command help |
| Network Peers | `/peers` | Full peer list with traffic stats, auto-refreshes every 10 s |
| Electrum Servers | `/electrum-servers` | Discovered ElectrumX peers with TCP/SSL reachability |

### Dashboard tabs

The main page (`/`) has five tabs that persist across reloads via `localStorage` and `#hash`:

| Tab | Contents |
|-----|----------|
| System Resources | CPU, memory, and disk usage with progress bars |
| BitcoinPurple Node | Block height, difficulty, network, sync progress, version, hashrate, connections → `/peers`, console → `/console` |
| ElectrumX Server | Version, uptime, DB size, server IP, TCP/SSL ports, active servers → `/electrum-servers` |
| Mempool | Transaction count, total size, memory usage |
| Recent Blocks | Last 10 blocks: height, hash, time, size, tx count |

---

## Authentication

| Client origin | Dashboard pages | API (`/api/*`) |
|---------------|-----------------|----------------|
| Localhost / LAN (RFC1918 private IPs) | No auth | No auth |
| External / public IP | HTTP Basic Auth | API key required |

### Configure external access

```bash
# From the project root:
./generate-api-key.sh    # prints a secure random key
cp .env.example .env
nano .env                # fill in the variables
```

`.env` variables:

| Variable | Used for |
|----------|---------|
| `DASHBOARD_AUTH_USERNAME` | Basic Auth username (dashboard pages, external clients) |
| `DASHBOARD_AUTH_PASSWORD` | Basic Auth password (dashboard pages, external clients) |
| `API_KEY` | API key for `/api/*` calls from external IPs; also signs session cookies |
| `DASHBOARD_SESSION_HOURS` | How long a login session lasts before re-authentication is required (default: `1`) |
| `DASHBOARD_SESSION_COOKIE_SECURE` | Set to `true` if the dashboard is served over HTTPS (default: `false`) |

After a successful login, the browser receives a signed session cookie valid for `DASHBOARD_SESSION_HOURS` hours. Navigating between pages does not trigger a new login prompt until the session expires.

After editing `.env`, apply it:
```bash
docker compose up -d --force-recreate dashboard
```

---

## REST API

All endpoints return JSON. No authentication is required from localhost or LAN.
External clients must pass the API key via header:

```bash
# Option A — custom header
curl -H "X-API-Key: <your-key>" http://<host>:8080/api/health

# Option B — Bearer token
curl -H "Authorization: Bearer <your-key>" http://<host>:8080/api/health
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Overall service health (`bitcoinpurple` + `electrumx` status) |
| `GET` | `/api/config` | Returns the configured `API_KEY` (requires session or API key auth) |
| `GET` | `/api/system/resources` | CPU, memory, and disk usage |
| `GET` | `/api/bitcoinpurple/info` | Node info: blockchain, network, mining, mempool |
| `GET` | `/api/bitcoinpurple/block-height` | Current block height |
| `GET` | `/api/bitcoinpurple/network-hashrate` | Network hashrate in H/s |
| `GET` | `/api/bitcoinpurple/difficulty` | Current network difficulty |
| `GET` | `/api/bitcoinpurple/coinbase-subsidy` | Current block subsidy in BTCP |
| `GET` | `/api/bitcoinpurple/peers` | Detailed peer list with traffic stats |
| `GET` | `/api/bitcoinpurple/blocks/recent` | Last 10 blocks (height, hash, time, size, tx count) |
| `GET` | `/api/electrumx/stats` | ElectrumX version, uptime, DB size, IP, ports, active servers |
| `GET` | `/api/electrumx/servers` | Discovered ElectrumX peers with TCP/SSL reachability |
| `POST` | `/api/cli` | Execute a read-only `bitcoinpurple-cli` command (see below) |
| `GET` | `/api/cli/methods` | List all methods allowed by `/api/cli` |

### `/api/cli` — Node Console API

Executes a whitelisted read-only RPC method against the node. The method must be in the
`CLI_READONLY_METHODS` frozenset (see `app.py`). Write operations are not permitted.

**Request:**
```json
{ "method": "getblockchaininfo", "params": [] }
```

**Success response:**
```json
{ "result": { ... } }
```

**RPC error response** (HTTP 200):
```json
{ "rpc_error": { "code": -5, "message": "Invalid address" } }
```

**Allowed methods (40+):**

| Category | Methods |
|----------|---------|
| Blockchain | `getbestblockhash`, `getblock`, `getblockchaininfo`, `getblockcount`, `getblockfilter`, `getblockhash`, `getblockheader`, `getblockstats`, `getchaintips`, `getchaintxstats`, `getdifficulty` |
| Mempool | `getmempoolancestors`, `getmempooldescendants`, `getmempoolentry`, `getmempoolinfo`, `getrawmempool` |
| UTXO / TX | `gettxout`, `gettxoutproof`, `gettxoutsetinfo`, `getrawtransaction`, `decoderawtransaction`, `decodescript`, `verifytxoutproof` |
| Network | `getnetworkinfo`, `getpeerinfo`, `getnettotals`, `getnetworkhashps`, `getconnectioncount`, `getaddednodeinfo`, `listbanned` |
| Mining | `getmininginfo`, `estimatesmartfee`, `estimaterawfee`, `getblocksubsidy` |
| Address | `validateaddress`, `getaddressinfo`, `verifymessage` |
| Node | `uptime`, `getindexinfo`, `logging` |

### Example calls

```bash
BASE="http://localhost:8080"          # local
# BASE="http://192.168.1.100:8080"   # LAN
# BASE="http://<public-ip>:8080"     # internet (add -H "X-API-Key: ..." )

# Health check
curl "$BASE/api/health" | jq

# Block height
curl "$BASE/api/bitcoinpurple/block-height" | jq

# Full node info
curl "$BASE/api/bitcoinpurple/info" | jq

# Run a CLI command
curl -X POST "$BASE/api/cli" \
  -H "Content-Type: application/json" \
  -d '{"method":"getblockchaininfo","params":[]}' | jq

# ElectrumX stats
curl "$BASE/api/electrumx/stats" | jq

# System resources
curl "$BASE/api/system/resources" | jq
```

### Common error responses

| Code | Body | Cause |
|------|------|-------|
| `400` | `{"error":"method is required"}` | Missing `method` in `/api/cli` body |
| `401` | `{"error":"Valid API key required"}` | Missing or wrong API key |
| `403` | `{"error":"Method \"...\" is not in the allowed read-only list"}` | `/api/cli` blocked method |
| `503` | `{"error":"API key is not configured"}` | `API_KEY` not set in `.env` |

---

## Test suite

Tests live in `test/` — see [`test/README.md`](../test/README.md) for full details.

```bash
# Unit tests — offline, no Docker needed
pytest test/unit/ -v

# Integration tests — requires docker compose up -d
pytest test/integration/ -v
```

---

## Technology stack

| Layer | Details |
|-------|---------|
| Backend | Python 3.11, Flask |
| Frontend | HTML5, CSS3 (custom responsive design), vanilla JavaScript |
| Pages | `index.html`, `console.html`, `peers.html`, `electrum_servers.html` |
| Static assets | `style.css`, `dashboard.js`, `console.js`, `peers.js`, `electrum_servers.js`, `bitcoinpurple.png` (favicon) |
| Container | `Dockerfile.dashboard`, port `8080` |
