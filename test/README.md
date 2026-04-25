# Tests

Three-layer test suite: unit tests run offline, integration and e2e tests require the Docker stack.

## Structure

```
test/
├── tools/
│   └── test-server.py           # Manual CLI: connects to ElectrumX and prints server info
├── unit/                        # Pure Python, no external dependencies (130 tests)
│   ├── test_coins_params.py     # All chain params in coins_btcp.py vs technical-data.md
│   ├── test_auth.py             # IP trust logic, API key, Basic Auth, X-Forwarded-For spoofing
│   ├── test_utils.py            # parse_services_ports, parse_addnode_hosts
│   ├── test_api_endpoints.py    # All /api/* endpoints — happy path + RPC/ElectrumX down
│   └── test_entrypoint.py       # entrypoint.sh: credential extraction, port fallback, DAEMON_URL
├── integration/                 # Auto-skipped if stack is not running (18 tests)
│   ├── test_node_rpc.py         # Node: getblockchaininfo, genesis hash, P2P port
│   ├── test_electrumx.py        # ElectrumX TCP + SSL: version strings, genesis, indexed blocks
│   └── test_dashboard.py        # Dashboard: services up, peers, sync state, resources range
└── e2e/                         # Builds and starts the stack automatically (9 tests)
    ├── test_stack_startup.py    # All containers running, no FATAL in logs
    └── test_electrum_protocol.py # Full Electrum handshake, headers subscribe
```

## Running Tests

### Unit (offline)

```bash
pip install -r test/requirements.txt
pytest test/unit/ -v
```

### Integration (stack must be running)

```bash
docker compose up -d
pytest test/integration/ -v
```

Integration tests auto-skip with a clear message if the stack is not up. They check real
server behavior, not just that processes are alive:

| Test | What it actually verifies |
|------|--------------------------|
| `test_health_both_services_up` | Both `bitcoinpurple` and `electrumx` report `up`, not just HTTP 200 |
| `test_node_headers_match_blocks` | `headers == blocks` — node is fully synced, not just started |
| `test_node_has_peers` | At least one P2P peer is connected — required for syncing |
| `test_tcp_server_version_strings` | `[server_ver, protocol_ver]` are both non-empty strings |
| `test_tcp_electrumx_has_indexed_blocks` | Block header at height 1 returns valid 160-char hex — proves ElectrumX has indexed the chain |
| `test_ssl_server_features_genesis` | Genesis hash over SSL matches mainnet exactly |
| `test_system_resources_in_valid_range` | CPU/memory/disk percent is in `[0, 100]`, not just `>= 0` |

### E2E (builds and starts the stack automatically)

```bash
pytest test/e2e/ -v
```

The e2e fixture runs `docker compose up -d --build`, waits up to 120 s for `/api/health`
to respond, runs the tests, then tears the stack down.

### Run everything

```bash
pytest test/unit/ test/integration/ -v   # unit + integration (stack must be up)
pytest test/ -v                          # all layers
```

## Design Notes

Integration tests are written to catch real failures, not just structural ones. A few examples
of what would have been false positives without the current checks:

- `percent >= 0` always passes — `0 <= percent <= 100` catches psutil returning garbage
- HTTP 200 on `/api/health` passes even when both services are `down` — status check required
- `isinstance(result, list)` passes for any list — length and non-empty string checks added
- `blocks > 0` passes even at block 1 — `blocks == headers` proves actual sync

## Manual Tools

`test/tools/test-server.py` is a standalone CLI client — not a pytest file. Use it to manually
inspect any ElectrumX server:

```bash
python test/tools/test-server.py localhost:51001   # TCP
python test/tools/test-server.py localhost:51002   # SSL (auto-detected by port)
python test/tools/test-server.py myserver.com:51002
```

Prints `server.version`, `server.features`, and the latest block height + hash.

---

## Pytest Markers

| Marker | When it runs |
|--------|-------------|
| `unit` | Always (offline) |
| `integration` | Requires `docker compose up -d` |
| `e2e` | Builds and starts stack automatically |

Run only one layer: `pytest test/unit/ -v`
