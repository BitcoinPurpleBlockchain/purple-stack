# Configuration

## Component versions

| Component | Version | Notes |
|-----------|---------|-------|
| **ElectrumX** | 1.18.0 | Package `e-x` from [spesmilo/electrumx](https://github.com/spesmilo/electrumx); base image `lukechilds/electrumx:latest` |
| **Python** (ElectrumX container) | 3.13.5 | Provided by the base image |
| **bitcoinpurpled** | see `daemon/download-binaries.sh` | Downloaded from [BitcoinPurpleBlockchain/bitcoinpurplecore](https://github.com/BitcoinPurpleBlockchain/bitcoinpurplecore/releases/latest) |

> The ElectrumX base image is not pinned to a specific tag. If a future `lukechilds/electrumx` release breaks compatibility, pin it in [Dockerfile.electrumx](../Dockerfile.electrumx): `FROM lukechilds/electrumx:<tag>`.

---

## Environment variables

Copy `.env.example` to `.env` and edit as needed. All variables have defaults and the file is optional for local/LAN-only setups.

### Ports

| Variable | Default | Description |
|----------|---------|-------------|
| `ELECTRUMX_TCP_PORT` | `51001` | ElectrumX plain TCP port |
| `ELECTRUMX_SSL_PORT` | `51002` | ElectrumX SSL port |
| `DASHBOARD_PORT` | `8080` | Web dashboard external port |

### Dashboard authentication

| Variable | Description |
|----------|-------------|
| `DASHBOARD_AUTH_USERNAME` | Basic Auth username for external clients |
| `DASHBOARD_AUTH_PASSWORD` | Basic Auth password for external clients |
| `API_KEY` | API key for `/api/*` from external IPs; also signs session cookies |
| `DASHBOARD_SESSION_HOURS` | Session duration after login (default: `1`) |
| `DASHBOARD_SESSION_COOKIE_SECURE` | Set `true` when serving over HTTPS |

### ElectrumX peer bootstrap

```ini
# Comma-separated list of known BTCP ElectrumX servers.
# Format: "host s t"  (s = SSL, t = TCP, using the default ports above)
# Example: ELECTRUMX_PEERS=1.2.3.4 s t,mynode.example.com s t
# ELECTRUMX_PEERS=
```

`bitcoinpurpleblockchain.com` is hardcoded as the network bootstrap peer — servers discover each other automatically once it is reachable. Set `ELECTRUMX_PEERS` only to add extra bootstrap nodes.

---

## Node configuration

Edit `.bitcoinpurple/bitcoinpurple.conf` directly.

> **Before starting the node**, change the RPC credentials — the defaults are placeholders and must not be used in production.

```ini
rpcuser=your_username
rpcpassword=your_strong_password
```

See `technical-data.md` §9 for the full annotated config reference.

---

## Testnet

1. Add to `.bitcoinpurple/bitcoinpurple.conf`:
   ```ini
   testnet=1
   rpcport=23495
   ```
2. In `docker-compose.yml`, electrumx service: set `NET: "testnet"`
3. Clear the ElectrumX index: `rm -rf ./electrumx-data/*`
4. Restart: `docker compose up -d`

---

## Backup

| What | Path |
|------|------|
| Blockchain data | `.bitcoinpurple/blocks/` · `.bitcoinpurple/chainstate/` |
| Wallet | `.bitcoinpurple/wallet.dat` |
| ElectrumX index | `electrumx-data/` |
| SSL certificates | `certs/` |

To bootstrap a fresh node from an existing synced copy:

```bash
cp -r ~/.bitcoinpurple/blocks     .bitcoinpurple/
cp -r ~/.bitcoinpurple/chainstate .bitcoinpurple/
cp -r ~/.bitcoinpurple/indexes    .bitcoinpurple/
```
