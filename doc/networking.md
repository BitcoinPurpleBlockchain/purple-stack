# Networking

## Architecture

```
Internet                  Docker host  (network: purple)
   │
   ├── :13496  P2P ──────► bitcoinpurpled
   │                              │ RPC :13495 (internal)
   ├── :50001  TCP ──────► electrumx ◄───────────────────┘
   ├── :50002  SSL ──────► electrumx
   │
   └── :8080   HTTP ─────► dashboard ◄── bitcoinpurpled + electrumx
```

All services communicate over the shared `purple` Docker network using their service hostnames. RPC, ZMQ, and ElectrumX admin ports are internal only — not reachable from outside the host.

---

## Internal endpoints

| Service | Hostname | Port | Protocol |
|---------|----------|------|----------|
| Node RPC | `bitcoinpurpled` | `13495` | JSON-RPC |
| ZMQ rawblock | `bitcoinpurpled` | `28332` | ZMQ pub |
| ZMQ rawtx | `bitcoinpurpled` | `28333` | ZMQ pub |
| ZMQ hashblock | `bitcoinpurpled` | `28334` | ZMQ pub |
| ZMQ hashtx | `bitcoinpurpled` | `28335` | ZMQ pub |
| ElectrumX TCP | `electrumx` | `50001` | Electrum |
| ElectrumX SSL | `electrumx` | `50002` | Electrum (SSL) |
| ElectrumX admin | `electrumx` | `8000` | JSON-RPC |
| Dashboard | `dashboard` | `8080` | HTTP |

---

## Port forwarding (public access)

Forward these ports on your router to the server's local IP (`hostname -I | awk '{print $1}'`):

| Port | Service | Notes |
|------|---------|-------|
| `13496` TCP | BitcoinPurple P2P | Required for node participation |
| `50001` TCP | ElectrumX plain | Electrum wallet connections |
| `50002` TCP | ElectrumX SSL | Recommended for public wallets |
| `8080` TCP | Dashboard | Only if exposing publicly — configure auth first |

---

## Connecting external Docker stacks

Other stacks on the same host can reach the node and ElectrumX by joining the `purple` network — no host ports need to be exposed.

```yaml
# your-stack/docker-compose.yml
networks:
  purple:
    external: true

services:
  myapp:
    networks:
      - purple
    environment:
      RPC_HOST: bitcoinpurpled
      RPC_PORT: "13495"
      ZMQ_RAWBLOCK:  "tcp://bitcoinpurpled:28332"
      ZMQ_RAWTX:     "tcp://bitcoinpurpled:28333"
      ZMQ_HASHBLOCK: "tcp://bitcoinpurpled:28334"
      ZMQ_HASHTX:    "tcp://bitcoinpurpled:28335"
      ELECTRUMX_HOST: electrumx
      ELECTRUMX_TCP_PORT: "50001"
      ELECTRUMX_SSL_PORT: "50002"
```

> Start `purple-stack` before any dependent stack. The `purple` network is created on first `docker compose up`.

### Exposing internal ports to the host

If an application runs directly on the host (not in Docker), add a port mapping in `docker-compose.yml`:

```yaml
ports:
  - "127.0.0.1:13495:13495"   # RPC — localhost only
  - "127.0.0.1:28332:28332"   # ZMQ rawblock — localhost only
```

Always bind to `127.0.0.1` for RPC and ZMQ. Never use `0.0.0.0` for these ports.
