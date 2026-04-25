# Troubleshooting

Always check logs first:

```bash
docker compose logs -f <service>   # bitcoinpurpled | electrumx | dashboard
```

---

## Containers not starting

Common causes: wrong binary architecture, incorrect RPC credentials, port already in use.

**Port conflict:**
```bash
sudo lsof -i :<port>
```
Override the conflicting port via the corresponding variable in `.env`.

**Wrong binary architecture:**
```bash
uname -m                    # expected: x86_64 or aarch64
file daemon/bitcoinpurpled  # must match
cd daemon && ./download-binaries.sh --platform linux --arch x86_64
```

---

## ElectrumX cannot connect to the node

Verify the node is running and credentials are correct:

```bash
docker exec bitcoinpurple-node bitcoinpurple-cli \
  -rpcuser=USER -rpcpassword=PASS getblockchaininfo
```

If this fails, check `rpcuser` and `rpcpassword` in `.bitcoinpurple/bitcoinpurple.conf`.

---

## Dashboard shows services as down

The node or ElectrumX may still be syncing or indexing — this can take hours to days on first run. Check logs and wait.

---

## Dashboard not reachable from LAN

```bash
sudo ufw allow ${DASHBOARD_PORT:-8080}/tcp
netstat -tln | grep 8080   # verify the port is listening on 0.0.0.0
```

---

## ElectrumX not discovering peers

Peer discovery requires at least one reachable bootstrap server. The stack ships with `bitcoinpurpleblockchain.com` hardcoded — verify it is reachable:

```bash
python3 -c "import socket; socket.create_connection(('bitcoinpurpleblockchain.com', 51002), timeout=5); print('OK')"
```

To add extra bootstrap peers, set `ELECTRUMX_PEERS` in `.env` (see [configuration.md](configuration.md)).
