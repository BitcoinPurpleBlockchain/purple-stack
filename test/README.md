# Tests

Three-layer test suite: unit tests run fully offline, integration and e2e tests require the
Docker stack.

---

## Setup

Create and activate a virtual environment once, then install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r test/requirements.txt
```

Always activate the venv before running tests:

```bash
source venv/bin/activate
```

> Running `pytest` without the venv active will use the system Python, which may lack
> the required plugins (e.g. `pytest-timeout`) and produce confusing errors.

---

## Structure

```
test/
├── requirements.txt             # All test dependencies (pytest, pytest-mock, pytest-timeout …)
├── conftest.py                  # Session-scoped Flask app + client fixtures
├── fixtures.py                  # Shared mock data: MOCK_RPC_DATA, MOCK_ELECTRUMX_STATS,
│                                #   local_env(), external_env()
├── tools/
│   └── test-server.py           # Manual CLI: connects to any ElectrumX and prints server info
├── unit/                        # Pure Python, no Docker required
│   ├── test_auth.py             # IP trust logic, API key, Basic Auth, X-Forwarded-For spoofing
│   ├── test_api_endpoints.py    # All /api/* endpoints — happy path + RPC/ElectrumX down
│   ├── test_coins_params.py     # Chain params in coins_btcp.py (genesis, ports, verbytes, HRP…)
│   ├── test_entrypoint.py       # entrypoint.sh: credential parsing, port fallback, DAEMON_URL
│   └── test_utils.py            # parse_services_ports(), parse_addnode_hosts()
├── integration/                 # Auto-skipped if stack is not running
│   ├── test_node_rpc.py         # Node: getblockchaininfo, genesis hash, P2P port
│   ├── test_electrumx.py        # ElectrumX TCP + SSL: version, genesis, indexed blocks
│   └── test_dashboard.py        # Dashboard: services up, peers, sync state, resources
└── e2e/                         # Builds and manages the stack automatically
    ├── conftest.py              # Fixture: docker compose up --build → wait healthy → tests → down
    ├── test_stack_startup.py    # All containers running, no FATAL in logs
    └── test_electrum_protocol.py # Full Electrum handshake, headers subscribe, clean disconnect
```

---

## Unit tests — offline, no Docker

```bash
pytest test/unit/ -v
```

These tests mock all external dependencies and run in under 10 seconds on any machine.

---

## Integration tests — stack must be running

```bash
docker compose up -d
pytest test/integration/ -v
```

The session fixture checks port 8080 at startup. If the stack is not up, all integration
tests are **automatically skipped** with a clear message — they will not fail.

### Custom ports

If your `.env` uses non-default ElectrumX ports, pass them as environment variables:

```bash
ELECTRUMX_TCP_PORT=55001 ELECTRUMX_SSL_PORT=55002 pytest test/integration/ -v
```

### Tests that depend on sync state

Some tests will **legitimately fail** until the node has finished syncing:

| Test | Passes when |
|------|-------------|
| `test_node_headers_match_blocks` | `blocks == headers` — node fully synced |
| `test_node_has_peers` | At least one P2P peer is connected |
| `test_tcp_electrumx_has_indexed_blocks` | ElectrumX has indexed at least block 1 |

These are not bugs — they are intentionally strict checks. Run the full integration suite
again once the node is synced.

### What each test actually verifies

| Test | What it verifies |
|------|-----------------|
| `test_health_both_services_up` | Both services report `up`, not just HTTP 200 |
| `test_node_headers_match_blocks` | Node is fully synced (not just started) |
| `test_node_has_peers` | At least one P2P peer connected — required for syncing |
| `test_tcp_server_version_strings` | `[server_ver, protocol_ver]` are both non-empty |
| `test_tcp_electrumx_has_indexed_blocks` | Block header at height 1 is valid 160-char hex |
| `test_ssl_server_features_genesis` | Genesis hash over SSL matches mainnet exactly |
| `test_system_resources_in_valid_range` | CPU/memory/disk percent is in `[0, 100]` |

---

## E2E tests — stack managed automatically

```bash
pytest test/e2e/ -v --timeout=180
```

The `conftest.py` fixture:
1. Runs `docker compose up -d --build` (rebuilds images if source changed)
2. Polls `/api/health` every 3 s until **all services report `up`** (up to 120 s)
3. Runs all e2e tests
4. **Tears the stack down** with `docker compose down` after the session

> **Note:** the stack is stopped at the end. If you need it running after the tests,
> restart it with `docker compose up -d`.

### Custom ports

```bash
ELECTRUMX_TCP_PORT=55001 ELECTRUMX_SSL_PORT=55002 pytest test/e2e/ -v --timeout=180
```

---

## Run everything

```bash
# Unit + integration (stack must be up)
pytest test/unit/ test/integration/ -v

# All layers (e2e will build/start/stop the stack)
pytest test/ -v --timeout=180
```

---

## Manual tool

`test/tools/test-server.py` is a standalone CLI client — not a pytest file. Use it to
manually inspect any ElectrumX server:

```bash
python test/tools/test-server.py localhost:50001   # TCP
python test/tools/test-server.py localhost:50002   # SSL (auto-detected by port)
python test/tools/test-server.py myserver.com:50002
```

Prints `server.version`, `server.features`, and the latest block height + hash.

---

## Pytest markers

| Marker | Layer | When it runs |
|--------|-------|-------------|
| `unit` | unit/ | Always (offline) |
| `integration` | integration/ | Requires `docker compose up -d`; skipped otherwise |
| `e2e` | e2e/ | Stack built and started automatically |

Run a single layer by marker:

```bash
pytest -m unit -v
pytest -m integration -v
pytest -m e2e -v --timeout=180
```
