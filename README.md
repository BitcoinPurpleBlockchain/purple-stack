# purple-stack

Production-ready Docker stack for **BitcoinPurple (BTCP)** — full node, ElectrumX server, and web dashboard in a single `docker compose up`.

| Service | Description | Default ports |
|---------|-------------|---------------|
| **bitcoinpurpled** | BitcoinPurple full node | `13496` P2P |
| **electrumx** | ElectrumX Electrum protocol server | `51001` TCP · `51002` SSL |
| **dashboard** | Real-time monitoring UI + REST API | `8080` HTTP |

**Requirements:** Docker 20.10+, Docker Compose 2.0+, 64-bit Linux/macOS/WSL2, 4 GB+ RAM, 50 GB+ disk.

---

## Quick Start

```bash
# 1. Download node binaries
cd daemon && ./download-binaries.sh

# 2. ⚠ Set RPC credentials in .bitcoinpurple/bitcoinpurple.conf
#    rpcuser=your_username                  ← change this
#    rpcpassword=your_strong_password       ← change this

# 3. Start
docker compose up -d
```

Dashboard: `http://localhost:8080`

For internet-facing deployments, configure auth before exposing port 8080:

```bash
cp .env.example .env
./generate-api-key.sh
nano .env
```

---

## Common Commands

```bash
docker compose up -d                 # start
docker compose down                  # stop
docker compose up -d --build         # rebuild after code changes
docker compose logs -f <service>     # tail logs

docker exec bitcoinpurple-node bitcoinpurple-cli \
  -rpcuser=USER -rpcpassword=PASS getblockchaininfo

# Tests (see test/README.md for full details)
pytest test/unit/ -v                 # offline, no stack needed
pytest test/integration/ -v         # requires docker compose up -d
```

---

## Documentation

| Doc | Contents |
|-----|----------|
| [doc/configuration.md](doc/configuration.md) | Environment variables, ports, node config, testnet, backup |
| [doc/networking.md](doc/networking.md) | Architecture, internal endpoints, port forwarding, external stacks |
| [doc/security.md](doc/security.md) | Auth model, SSL certificates, firewall |
| [doc/troubleshooting.md](doc/troubleshooting.md) | Common issues and fixes |
| [web-dashboard/README.md](web-dashboard/README.md) | Dashboard features and REST API reference |
| [technical-data.md](technical-data.md) | Full BTCP chain parameters reference |
| [test/README.md](test/README.md) | Test suite: unit, integration, e2e |

---

## License

MIT — see [LICENSE](LICENSE).

Built on [kyuupichan/electrumx](https://github.com/kyuupichan/electrumx) and [BitcoinPurpleBlockchain/bitcoinpurplecore](https://github.com/BitcoinPurpleBlockchain/bitcoinpurplecore).
