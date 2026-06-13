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

Peer discovery requires at least one reachable bootstrap server. The stack ships with five hardcoded bootstrap peers (see `entrypoint.sh` `BUILTIN_PEERS`). Verify at least one is reachable:

```bash
python3 -c "import socket; socket.create_connection(('bitcoinpurpleblockchain.com', 50002), timeout=5); print('OK')"
```

To add extra bootstrap peers, set `ELECTRUMX_PEERS` in `.env` (see [configuration.md](configuration.md)).

---

## ElectrumX crash-loop: `struct.error: 'H' format requires 0 <= number <= 65535`

ElectrumX stores the history DB *flush counter* as a 16-bit unsigned integer (max **65535**).
When an index reaches the limit (startup log shows `flush count: 65,535`), the next flush
overflows, the server terminates with the `struct.error` above, and Docker restarts it into the
same crash — a loop.

The counter lives inside `electrumx-data/`, not in the code, so this can hit one host and not
another with the same repo. The stack **self-heals**: `entrypoint.sh` reads the flush counter
before starting the server and, when it is near the limit, resets it automatically — preferring
non-destructive `electrumx_compact_history`, falling back to wiping the index for a clean resync
(the index is derived data, always rebuildable from the node).

The threshold is configurable via `FLUSH_COMPACT_THRESHOLD` (default `60000`). To force the fix
immediately, just restart the stack; the guard runs on every ElectrumX startup. Equivalent
manual fix:

```bash
docker compose stop electrumx
rm -rf electrumx-data/*
docker compose up -d
```

---

## Node Console shows "method not allowed"

The `/console` page only exposes read-only RPC methods. Write operations (`sendrawtransaction`, `generate`, etc.) are intentionally blocked. Use `bitcoinpurple-cli` directly inside the container for write operations:

```bash
docker exec bitcoinpurple-node bitcoinpurple-cli \
  -rpcuser=USER -rpcpassword=PASS <command>
```
