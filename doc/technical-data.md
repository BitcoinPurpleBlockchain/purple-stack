# BitcoinPurple — Technical Reference

Parameter reference for BitcoinPurple (BTCP) node operators and developers building
on top of the network: ElectrumX server, Electrum wallet fork, Lightning Network fork.
All values are sourced directly from the codebase unless noted otherwise.

---

## Quick Reference

The most-looked-up values, all in one place.

| Parameter | Mainnet | Testnet | Signet | Regtest |
|-----------|---------|---------|--------|---------|
| P2P port | `13496` | `23496` | `33496` | `18444` |
| RPC port | `13495` | `23495` | `33495` | `18443` |
| ElectrumX TCP | `50001` | `60001` | — | — |
| ElectrumX SSL | `50002` | `60002` | — | — |
| Magic bytes | `fc991395` | `29fbc5fe` | — | `31346ac9` |
| Bech32 / BOLT11 HRP | `btcp` | `tbtcp` | `tbtcp` | `rbtcp` |
| P2PKH prefix | 56 (`0x38`) → `P` | 56 (`0x38`) | 56 | 56 |
| P2SH prefix | 55 (`0x37`) → `P` | 55 (`0x37`) | 55 | 55 |
| WIF prefix | 183 (`0xb7`) | 183 (`0xb7`) | 183 | 183 |
| BIP32 xpub | `0488B21E` | `043587CF` | `043587CF` | `043587CF` |
| BIP32 xprv | `0488ADE4` | `04358394` | `04358394` | `04358394` |
| Block time | 60 s | 60 s | 60 s | instant |
| Halving interval | 500,000 blocks | — | — | 150 blocks |
| Monetary cap (`MAX_MONEY`) | 1,000,000 BTCP | — | — | — |
| Genesis hash | `000003823f…c015` | `000002fdc3…d998` | `00000131aa…b403` | `6f6ffbda…e1df` |
| LN chain_hash | `15c04ef0…0000` | `98d9f92e…0000` | — | — |

---

## 1. Network Identity

| Parameter | Value | Source |
|-----------|-------|--------|
| Full name | BitcoinPurple | — |
| Ticker | BTCP | — |
| Version | 1.1.1 | `configure.ac` |
| Daemon binary | `bitcoinpurpled` | — |
| Config file | `~/.bitcoinpurple/bitcoinpurple.conf` | — |
| PoW algorithm | SHA256d (identical to Bitcoin) | — |
| Protocol version | 70016 | `src/version.h:12` |
| Min peer protocol | 31800 | `src/version.h:18` |

---

## 2. Mainnet Parameters

### 2.1 Ports

| Service | Port | Source |
|---------|------|--------|
| P2P | `13496` | `src/kernel/chainparams.cpp:116` |
| RPC | `13495` | `src/chainparamsbase.cpp:47` |
| Tor onion | `8334` | `src/chainparamsbase.cpp:47` |

### 2.2 Address Encoding

| Type | Decimal | Hex | Address prefix | Source |
|------|---------|-----|----------------|--------|
| P2PKH (`PUBKEY_ADDRESS`) | 56 | `0x38` | `P` | `src/kernel/chainparams.cpp:154` |
| P2SH (`SCRIPT_ADDRESS`) | 55 | `0x37` | `P` | `src/kernel/chainparams.cpp:155` |
| WIF secret key | 183 | `0xb7` | — | `src/kernel/chainparams.cpp:156` |
| Bech32 HRP | — | — | `btcp1…` | `src/kernel/chainparams.cpp:160` |

### 2.3 HD Key Version Bytes

**BIP32 standard (xpub / xprv):**

| Type | Bytes (hex) | Base58 prefix | Source |
|------|-------------|---------------|--------|
| xpub | `0488B21E` | `xpub` | `src/kernel/chainparams.cpp:157` |
| xprv | `0488ADE4` | `xprv` | `src/kernel/chainparams.cpp:158` |

**SLIP-0132 extended headers (all script types):**

BTCP uses the same BIP32 root bytes as Bitcoin mainnet, so the registered
SLIP-0132 SegWit version bytes are identical to Bitcoin mainnet. Taproot/BIP86
does **not** have registered SLIP-0132 `trub` / `trpv` headers; use standard
`xpub` / `xprv` plus the BIP86 derivation path or descriptors.

```python
XPRV_HEADERS = {
    'standard':    0x0488ade4,  # xprv
    'p2wpkh-p2sh': 0x049d7878,  # yprv
    'p2wsh-p2sh':  0x0295b005,  # Yprv
    'p2wpkh':      0x04b2430c,  # zprv
    'p2wsh':       0x02aa7a99,  # Zprv
}
XPUB_HEADERS = {
    'standard':    0x0488b21e,  # xpub
    'p2wpkh-p2sh': 0x049d7cb2,  # ypub
    'p2wsh-p2sh':  0x0295b43f,  # Ypub
    'p2wpkh':      0x04b24746,  # zpub
    'p2wsh':       0x02aa7ed3,  # Zpub
}
```

### 2.4 Magic Bytes (P2P message header)

`fc 99 13 95` — Source: `src/kernel/chainparams.cpp:112-115`

### 2.5 Genesis Block

| Parameter | Value | Source |
|-----------|-------|--------|
| Hash (display) | `000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015` | `src/kernel/chainparams.cpp:144` |
| LN chain_hash (wire, reversed bytes) | `15c04ef0bc1856d6b1ec199ca25d0aa7e77c6114e2cb0649ea82bf3f82030000` | derived |
| Merkle root | `b5f46757618a0aa2961b23f51de039ef23a77c24decc43d600348aff051f0a05` | `src/kernel/chainparams.cpp:145` |
| Timestamp (Unix) | `1691126832` | `src/kernel/chainparams.cpp:121` |
| Timestamp (UTC) | `2023-08-04T05:27:12Z` | — |
| Nonce | `1302816` (`0x13E120`) | `src/kernel/chainparams.cpp:121` |
| nBits | `1e0ffff0` | `src/kernel/chainparams.cpp:121` |
| Version | `1` | `src/kernel/chainparams.cpp:121` |
| Coinbase message | `"Global transactions for everyone around the world"` | `src/kernel/chainparams.cpp:64` |
| Coinbase pubkey | `04f26c8111029cf40de900c7075706cb58e5ed1e7f1d4911790019ee8c345eeb84060b1a09fb655c88e58ff35357ffe28678e62008f759ea260c7c37c9fae23869` | `src/kernel/chainparams.cpp:65` |

### 2.6 Consensus & Emission

| Parameter | Value | Source |
|-----------|-------|--------|
| Block time (`nPowTargetSpacing`) | 60 seconds | `src/kernel/chainparams.cpp:88` |
| Difficulty retarget window | 120 blocks (~2 hours) | `src/kernel/chainparams.cpp:87-88` |
| PoW target timespan | 7200 seconds | `src/kernel/chainparams.cpp:87` |
| PoW limit | `00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff` | `src/kernel/chainparams.cpp:86` |
| Halving interval | 500,000 blocks | `src/kernel/chainparams.cpp:78` |
| Initial block reward | 1 BTCP | `src/validation.cpp:1549` |
| COIN (satoshis per BTCP) | 100,000,000 | `src/consensus/amount.h:16` |
| MAX_MONEY validation cap | 1,000,000 BTCP | `src/consensus/amount.h:27` |
| Coinbase maturity | 100 blocks | `src/consensus/consensus.h:19` |
| Rule change activation threshold | 108 / 120 blocks (90%) | `src/kernel/chainparams.cpp:91` |

**Block reward schedule** (source: `src/validation.cpp:1542-1551`):

| Era | Block range | Reward | Era total |
|-----|-------------|--------|-----------|
| 0 | 0 – 499,999 | 1.00000000 BTCP | 500,000 BTCP |
| 1 | 500,000 – 999,999 | 0.50000000 BTCP | 250,000 BTCP |
| 2 | 1,000,000 – 1,499,999 | 0.25000000 BTCP | 125,000 BTCP |
| 3 | 1,500,000 – 1,999,999 | 0.12500000 BTCP | 62,500 BTCP |
| ∞ | — | — | ~1,000,000 BTCP generated subsidy |

`MAX_MONEY` is the consensus money-range sanity cap, not a direct UTXO supply
counter. The genesis coinbase follows the normal 1 BTCP subsidy construction,
but like Bitcoin Core-derived chains it is not spendable from the UTXO set.
For user-facing supply text, distinguish:

- **Maximum generated subsidy:** asymptotically ~1,000,000 BTCP.
- **Maximum spendable subsidy:** asymptotically ~999,999 BTCP if the genesis
  coinbase remains unspendable.

### 2.7 Difficulty Adjustment

BTCP keeps Bitcoin's compact target / SHA256d proof-of-work validation, but the
retarget interval is much shorter:

| Parameter | Mainnet value | Source |
|-----------|---------------|--------|
| Target spacing | 60 seconds | `src/kernel/chainparams.cpp:88` |
| Target timespan | 7,200 seconds | `src/kernel/chainparams.cpp:87` |
| Adjustment interval | 120 blocks | `nPowTargetTimespan / nPowTargetSpacing` |
| Retarget boundary | every block height divisible by 120 | `src/pow.cpp:18-47` |
| Minimum actual timespan | 1,800 seconds | `src/pow.cpp:56` |
| Maximum actual timespan | 28,800 seconds | `src/pow.cpp:58` |
| Max change per retarget | 4x easier or 4x harder | `src/pow.cpp:56-66` |
| Mainnet min-difficulty blocks | disabled | `fPowAllowMinDifficultyBlocks=false` |
| No-retarget mode | disabled | `fPowNoRetargeting=false` |

Retarget flow for a candidate block at height `H`:

1. If `H % 120 != 0`, the block must keep the previous block's `nBits`.
2. If `H % 120 == 0`, take the previous 120-block window:
   `first = H - 120`, `last = H - 1`.
3. Compute `actual_timespan = last.time - first.time`.
4. Clamp it to `[7200 / 4, 7200 * 4]`, i.e. `[1800, 28800]` seconds.
5. Decode previous `nBits` to a target, then:

```text
new_target = old_target * actual_timespan / 7200
new_target = min(new_target, powLimit)
new_nBits  = compact(new_target)
```

Interpretation:

- Blocks faster than 60 seconds make `actual_timespan < 7200`, so target
  decreases and difficulty increases.
- Blocks slower than 60 seconds make `actual_timespan > 7200`, so target
  increases and difficulty decreases.
- The clamp prevents a single retarget from changing difficulty by more than 4x.

### 2.8 Soft-Fork Activation

All soft-forks are active from genesis (height 0). Source: `src/kernel/chainparams.cpp:79-102`

| BIP | Feature | Activation height |
|-----|---------|-------------------|
| BIP34 | Block height in coinbase | 0 |
| BIP65 | `CHECKLOCKTIMEVERIFY` | 0 |
| BIP66 | Strict DER signatures | 0 |
| BIP68/112/113 | `CheckSequenceVerify` (CSV) | 0 |
| BIP141/143/147 | SegWit | 0 |
| BIP340-342 | Taproot (`ALWAYS_ACTIVE`) | 0 |

### 2.9 Chain Validation

| Parameter | Value | Source |
|-----------|-------|--------|
| Minimum chain work | `00000000000000000000000000000000000000000000074e7000dc41ac550926` | `src/kernel/chainparams.cpp:104` |
| Default assume valid | `00000000000009733cf805e87e19261ae833319b874c694d4d74995ea526c968` | `src/kernel/chainparams.cpp:105` |
| Prune after height | 100,000 | `src/kernel/chainparams.cpp:117` |
| TX count reference | 1,189,400 at block 1,048,808 | `src/kernel/chainparams.cpp:178-184` |

### 2.10 DNS Seeds

| Seed | Source |
|------|--------|
| `node3.walletbuilders.com` | `src/kernel/chainparams.cpp:152` |

---

## 3. Testnet Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| P2P port | `23496` | `src/kernel/chainparams.cpp:230` |
| RPC port | `23495` | `src/chainparamsbase.cpp:49` |
| Magic bytes | `29 fb c5 fe` | `src/kernel/chainparams.cpp:226-229` |
| Bech32 / BOLT11 HRP | `tbtcp` | `src/kernel/chainparams.cpp:270` |
| P2PKH | 56 (`0x38`) | `src/kernel/chainparams.cpp:264` |
| P2SH | 55 (`0x37`) | `src/kernel/chainparams.cpp:265` |
| WIF prefix | 183 (`0xb7`) | `src/kernel/chainparams.cpp:266` |
| BIP32 xpub | `043587CF` | `src/kernel/chainparams.cpp:267` |
| BIP32 xprv | `04358394` | `src/kernel/chainparams.cpp:268` |
| Genesis hash (display) | `000002fdc3921c1ad368816fcc587f499698d42b42ab5a5d94ee67882ef9d998` | `src/kernel/chainparams.cpp:259` |
| LN chain_hash (wire) | `98d9f92e8867ee945d5aab422bd49896497f58cc6f8168d31a1c92c3fd020000` | derived |
| Genesis merkle root | `b5f46757618a0aa2961b23f51de039ef23a77c24decc43d600348aff051f0a05` | same as mainnet |
| Genesis timestamp | `1691126837` | `src/kernel/chainparams.cpp:235` |
| Genesis nonce | `521609` (`0x7F589`) | `src/kernel/chainparams.cpp:235` |
| Genesis nBits | `1e0ffff0` | `src/kernel/chainparams.cpp:235` |
| ElectrumX TCP / SSL | `60001` / `60002` | `coins_btcp.py` |

**SLIP-0132 HD headers — testnet** (identical to Bitcoin testnet, since BIP32 bytes are `043587CF`/`04358394`; Taproot/BIP86 still uses standard `tpub` / `tprv` plus path/descriptor metadata):

```python
XPRV_HEADERS = {
    'standard':    0x04358394,  # tprv
    'p2wpkh-p2sh': 0x044a4e28,  # uprv
    'p2wsh-p2sh':  0x024285b5,  # Uprv
    'p2wpkh':      0x045f18bc,  # vprv
    'p2wsh':       0x02575048,  # Vprv
}
XPUB_HEADERS = {
    'standard':    0x043587cf,  # tpub
    'p2wpkh-p2sh': 0x044a5262,  # upub
    'p2wsh-p2sh':  0x024289ef,  # Upub
    'p2wpkh':      0x045f1cf6,  # vpub
    'p2wsh':       0x02575483,  # Vpub
}
```

---

## 4. Signet Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| P2P port | `33496` | `src/kernel/chainparams.cpp:375` |
| RPC port | `33495` | `src/chainparamsbase.cpp:51` |
| Bech32 HRP | `tbtcp` | `src/kernel/chainparams.cpp:412` |
| P2PKH / P2SH / WIF | 56 / 55 / 183 | `src/kernel/chainparams.cpp:406-408` |
| BIP32 xpub / xprv | `043587CF` / `04358394` | `src/kernel/chainparams.cpp:409-410` |
| Genesis hash | `00000131aa3124412b7ba8473f137922692c88da8fe26042e250c6cd76b7b403` | `src/kernel/chainparams.cpp:402` |
| Genesis timestamp | `1691126842` | `src/kernel/chainparams.cpp:378` |
| Genesis nonce | `1829993` (`0x1be0a9`) | `src/kernel/chainparams.cpp:378` |
| Genesis nBits | `1e0377ae` | `src/kernel/chainparams.cpp:378` |
| PoW limit | `00000377ae000000000000000000000000000000000000000000000000000000` | `src/kernel/chainparams.cpp:350` |
| Default signet challenge | `512103ad5e0edad18cb1f0fc0d28a3d4f1f3e445640337489abb10404f2d1e086be430210359ef5021964fe22d6f8e05b2463c9540ce96883fe3b278760f048f5189f2e6c452ae` | `src/kernel/chainparams.cpp:308` |

---

## 5. Regtest Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| P2P port | `18444` | `src/kernel/chainparams.cpp:466` |
| RPC port | `18443` | `src/chainparamsbase.cpp:53` |
| Magic bytes | `31 34 6a c9` | `src/kernel/chainparams.cpp:462-465` |
| Bech32 HRP | `rbtcp` | `src/kernel/chainparams.cpp:556` |
| P2PKH / P2SH / WIF | 56 / 55 / 183 | `src/kernel/chainparams.cpp:550-552` |
| BIP32 xpub / xprv | `043587CF` / `04358394` | `src/kernel/chainparams.cpp:553-554` |
| Genesis hash | `6f6ffbda4cb789c69d885d4624ea4a28841d3689fbaf969262150ca45a1ae1df` | `src/kernel/chainparams.cpp:521` |
| Genesis timestamp | `1691126837` | `src/kernel/chainparams.cpp:497` |
| Genesis nonce | `4` | `src/kernel/chainparams.cpp:497` |
| Genesis nBits | `207fffff` | `src/kernel/chainparams.cpp:497` |
| Halving interval | 150 blocks | `src/kernel/chainparams.cpp:433` |
| No retargeting | `true` | `src/kernel/chainparams.cpp:440` |

---

## 6. ElectrumX Server

| Component | Version |
|-----------|---------|
| ElectrumX (`e-x`) | **1.18.0** — [spesmilo/electrumx](https://github.com/spesmilo/electrumx) |
| Python (container) | **3.13.5** |
| Base Docker image | `lukechilds/electrumx:latest` (unpinned) |

### 6.1 Coin Definition (`coins_btcp.py`)

Drop-in patch for `electrumx/lib/coins.py`. Place as
`electrumx-patch/coins_btcp.py` and apply via the Docker patch snippet below.

```python
# coins_btcp.py — BitcoinPurple (BTCP) coin definitions for ElectrumX
# Patch into electrumx/lib/coins.py alongside the Bitcoin class.


class BitcoinPurple(Bitcoin):
    NAME = 'BitcoinPurple'
    SHORTNAME = 'BTCP'
    NET = 'mainnet'
    DESERIALIZER = lib_tx.DeserializerSegWit
    GENESIS_HASH = (
        '000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015'
    )
    # Base58 address prefixes
    P2PKH_VERBYTE = bytes([56])       # 0x38
    P2SH_VERBYTES = (bytes([55]),)    # 0x37
    WIF_BYTE = bytes([183])           # 0xb7
    # BIP32 HD key version bytes
    XPUB_VERBYTES = bytes.fromhex('0488B21E')
    XPRV_VERBYTES = bytes.fromhex('0488ADE4')
    # Bech32 / SegWit metadata for forks; ElectrumX indexes scripts directly.
    SEGWIT_HRP = 'btcp'
    # Do not inherit Bitcoin Electrum peers or Bitcoin Core version gates.
    PEERS = []
    MIN_REQUIRED_DAEMON_VERSION = '1.1.1'
    BLACKLIST_URL = None
    # 1-minute blocks: keep enough undo data for practical reorg handling.
    REORG_LIMIT = 1200
    # Chain stats — updated from fully synced mainnet node at block 1,048,808 (Apr 2026)
    TX_COUNT = 1_189_400
    TX_COUNT_HEIGHT = 1_048_808
    TX_PER_BLOCK = 2
    # RPC port (bitcoinpurpled mainnet default)
    RPC_PORT = 13495
    PEER_DEFAULT_PORTS = {'t': '50001', 's': '50002'}


class BitcoinPurpleTestnet(BitcoinPurple):
    NAME = 'BitcoinPurple Testnet'
    SHORTNAME = 'TBTCP'
    NET = 'testnet'
    GENESIS_HASH = (
        '000002fdc3921c1ad368816fcc587f499698d42b42ab5a5d94ee67882ef9d998'
    )
    XPUB_VERBYTES = bytes.fromhex('043587CF')
    XPRV_VERBYTES = bytes.fromhex('04358394')
    SEGWIT_HRP = 'tbtcp'
    TX_COUNT = 1
    TX_COUNT_HEIGHT = 0
    TX_PER_BLOCK = 1
    RPC_PORT = 23495
    PEERS = []
    REORG_LIMIT = 1200
    PEER_DEFAULT_PORTS = {'t': '60001', 's': '60002'}
```

Notes for this coin class:

- `PEERS = []` is intentional until there are known-good BTCP ElectrumX peers.
  ElectrumX peer discovery verifies genesis, but inheriting Bitcoin peers wastes
  resources and can leak confusing peer data.
- `MIN_REQUIRED_DAEMON_VERSION` must not inherit Bitcoin's current upstream
  requirement. Keep it aligned with the BTCP daemon version you ship, or remove
  the version gate in your ElectrumX fork.
- `TX_COUNT`, `TX_COUNT_HEIGHT`, and `TX_PER_BLOCK` are sync-estimation hints,
  not consensus values. Refresh them from a synced BTCP node before release.
- ElectrumX does not need ZMQ to index; it polls RPC. ZMQ is useful for lower
  latency only if your chosen ElectrumX build/plugin uses it.

### 6.1.1 ElectrumX Node Requirements

Required full-node settings:

| Requirement | Value / setting | Reason |
|-------------|-----------------|--------|
| RPC server | `server=1`, `rpcport=13495` | ElectrumX reads blocks and transactions through JSON-RPC |
| Transaction index | `txindex=1` | Required for historical transaction lookups |
| Pruning | disabled (`prune=0`) | ElectrumX must be able to index from genesis |
| Chain | mainnet unless `NET=testnet` | Must match `COIN`/`NET` in ElectrumX |
| Disk | full block data + ElectrumX DB | DB grows with history; do not run from a tiny volume |

Minimum RPC methods used by ElectrumX-compatible servers include
`getblockhash`, `getblock`, `getrawtransaction`, `getnetworkinfo`,
`getblockchaininfo`, `estimatesmartfee`, and `sendrawtransaction`.

Recommended public Electrum services:

| Service | Mainnet | Testnet | Notes |
|---------|---------|---------|-------|
| Plain TCP | `50001` | `60001` | Standard Electrum convention |
| TLS/SSL TCP | `50002` | `60002` | Recommended for public wallets |
| Local admin RPC | `8000` | `8000` or private | Keep firewalled; do not advertise publicly |

For `servers.json`, replace `your-server.example.com` with a real DNS name or
public IP. The current file only documents the format; it does not configure a
real public server.

### 6.2 Docker Patch Snippet

```dockerfile
COPY electrumx-patch/coins_btcp.py /tmp/coins_btcp.py

RUN python3 - <<'PATCH'
import pathlib, re

patch = pathlib.Path('/tmp/coins_btcp.py').read_text()
classes = re.split(r'^(?=class )', patch, flags=re.MULTILINE)
classes = [c for c in classes if c.strip().startswith('class ')]
body = '\n' + '\n'.join(classes)

for target in [
    '/usr/local/lib/python3.13/dist-packages/electrumx/lib/coins.py',
    '/electrumx/src/electrumx/lib/coins.py',
]:
    p = pathlib.Path(target)
    if p.exists():
        s = p.read_text()
        if 'class BitcoinPurple(Bitcoin):' not in s:
            p.write_text(s + body)

print('>> Patched ElectrumX with BitcoinPurple coin classes')
PATCH
```

### 6.3 Environment Variables

```env
# ── Identity ──────────────────────────────────────────────────────────────────
COIN=BitcoinPurple
NET=mainnet                          # or: testnet

# ── Node connection ───────────────────────────────────────────────────────────
DAEMON_URL=http://btcpuser:CHANGE_ME@bitcoinpurpled:13495/
# testnet:  DAEMON_URL=http://btcpuser:CHANGE_ME@bitcoinpurpled:23495/

# ── Storage ───────────────────────────────────────────────────────────────────
DB_DIRECTORY=/data/electrumx

# ── Services exposed ──────────────────────────────────────────────────────────
SERVICES=tcp://0.0.0.0:50001,ssl://0.0.0.0:50002,rpc://0.0.0.0:8000
# Override only if auto-detected public IP is wrong:
# REPORT_SERVICES=tcp://your-server-ip:50001,ssl://your-server-ip:50002

# ── TLS ───────────────────────────────────────────────────────────────────────
SSL_CERTFILE=/certs/server.crt
SSL_KEYFILE=/certs/server.key

# ── Performance ───────────────────────────────────────────────────────────────
CACHE_MB=1200
MAX_SESSIONS=1000
INITIAL_CONCURRENT=2

# ── Rate limiting (0 = disabled) ─────────────────────────────────────────────
COST_SOFT_LIMIT=0
COST_HARD_LIMIT=0

# ── Peer discovery ────────────────────────────────────────────────────────────
PEER_DISCOVERY=on
PEER_ANNOUNCE=true
```

**Protocol version** served: `1.4.2`

**OS ulimit** — set `nofile` to at least `1048576` (open file descriptors):

```yaml
ulimits:
  nofile:
    soft: 1048576
    hard: 1048576
```

### 6.4 ZMQ Notification Ports

These are recommended local ports if you enable ZMQ notifications. BitcoinPurple
Core does not assign default ZMQ bind ports; the port only exists if you set the
corresponding `bitcoinpurple.conf` value.

| `bitcoinpurple.conf` key | Recommended local port | Payload |
|--------------------------|------------------------|---------|
| `zmqpubrawblock` | `28332` | full serialised block |
| `zmqpubrawtx` | `28333` | raw transaction (mempool + confirmed) |
| `zmqpubhashblock` | `28334` | 32-byte block hash |
| `zmqpubhashtx` | `28335` | 32-byte tx hash |

Prevent dropped messages under load:

```ini
zmqpubrawblockhwm=500
zmqpubrawtxhwm=500
```

---

## 7. Electrum Wallet (`constants.py`)

Reference for building an Electrum wallet fork targeting BTCP.
Modelled after the `AbstractNet` interface (see `pallectrum` for a working example).

### 7.1 Parameter Table

| Field | Mainnet | Testnet | Source / Note |
|-------|---------|---------|---------------|
| `NET_NAME` | `"bitcoinpurple"` | `"testnet"` | wallet data subfolder |
| `TESTNET` | `False` | `True` | |
| `WIF_PREFIX` | `0xb7` (183) | `0xb7` (183) | same on both — `chainparams.cpp:156/266` |
| `ADDRTYPE_P2PKH` | `56` | `56` | addresses start with `P` |
| `ADDRTYPE_P2SH` | `55` | `55` | addresses start with `P` |
| `SEGWIT_HRP` | `"btcp"` | `"tbtcp"` | Bech32 human-readable part |
| `BOLT11_HRP` | `"btcp"` | `"tbtcp"` | LN invoice prefix |
| `GENESIS` | `000003823f…c015` | `000002fdc3…d998` | full hashes in §2.5 / §3 |
| `DEFAULT_PORTS` | `{'t':'50001','s':'50002'}` | `{'t':'60001','s':'60002'}` | |
| `BIP44_COIN_TYPE` | **TBD / private project constant** | `1` | not registered for BitcoinPurple — see note |
| `LN_REALM_BYTE` | `0` | `1` | LN DNS realm byte; unused while `LN_DNS_SEEDS=[]` |
| `LN_DNS_SEEDS` | `[]` | `[]` | no LN seeds configured |
| `SKIP_POW_DIFFICULTY_VALIDATION` | `False` only after BTCP retarget support | `False` only after BTCP retarget support | see §7.7 |
| `POW_TARGET_SPACING` | `60` | `60` | seconds per block |
| `COINBASE_MATURITY` | `100` | `100` | blocks before coinbase is spendable |
| `BLOCK_HEIGHT_FIRST_LIGHTNING_CHANNELS` | `0` | `0` | allowed from genesis if LN is enabled |

> **BIP44 coin type:** BitcoinPurple has no SLIP-0044 entry. `BTCP` at index
> `183` is already assigned to Bitcoin Private, so do not reuse it for
> BitcoinPurple. In Electrum constants, store the non-hardened index
> (`0 <= value < 0x80000000`); wallet derivation code adds the hardened bit when
> building paths such as `m/44'/COIN_TYPE'/0'`. Use one project-wide provisional
> integer until an official SLIP-0044 slot is registered. The `13496` value below
> is a project-local placeholder chosen to match the BTCP P2P port, not a
> registered SLIP-0044 value.

### 7.2 `constants.py` Class Definitions

```python
# constants.py — BitcoinPurple network definitions for an Electrum wallet fork
# Drop these classes into electrum/constants.py alongside BitcoinMainnet.


class BitcoinPurple(AbstractNet):

    NET_NAME = "bitcoinpurple"
    TESTNET = False

    # Address & key encoding
    WIF_PREFIX = 0xb7           # 183 — chainparams.cpp:156
    ADDRTYPE_P2PKH = 56         # 0x38 — chainparams.cpp:154
    ADDRTYPE_P2SH = 55          # 0x37 — chainparams.cpp:155
    SEGWIT_HRP = "btcp"         # chainparams.cpp:160
    BOLT11_HRP = SEGWIT_HRP

    GENESIS = "000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015"
    DEFAULT_PORTS = {'t': '50001', 's': '50002'}

    # Consensus
    COINBASE_MATURITY = 100     # consensus/consensus.h:19
    POW_TARGET_SPACING = 60     # 60-second blocks

    # BIP44 coin type — not registered in SLIP-0044
    BIP44_COIN_TYPE = 13496       # provisional private constant; update when registered

    # Lightning. Height 0 means "allowed from genesis" in Electrum.
    BLOCK_HEIGHT_FIRST_LIGHTNING_CHANNELS = 0
    LN_REALM_BYTE = 0
    LN_DNS_SEEDS = []

    # PoW validation — requires BTCP's 120-block retarget implementation.
    SKIP_POW_DIFFICULTY_VALIDATION = False

    # SLIP-0132 HD key version bytes — identical to Bitcoin mainnet
    # BTCP mainnet uses the same BIP32 root bytes: 0488B21E / 0488ADE4
    XPRV_HEADERS = {
        'standard':    0x0488ade4,  # xprv
        'p2wpkh-p2sh': 0x049d7878,  # yprv
        'p2wsh-p2sh':  0x0295b005,  # Yprv
        'p2wpkh':      0x04b2430c,  # zprv
        'p2wsh':       0x02aa7a99,  # Zprv
    }
    XPRV_HEADERS_INV = inv_dict(XPRV_HEADERS)
    XPUB_HEADERS = {
        'standard':    0x0488b21e,  # xpub
        'p2wpkh-p2sh': 0x049d7cb2,  # ypub
        'p2wsh-p2sh':  0x0295b43f,  # Ypub
        'p2wpkh':      0x04b24746,  # zpub
        'p2wsh':       0x02aa7ed3,  # Zpub
    }
    XPUB_HEADERS_INV = inv_dict(XPUB_HEADERS)


class BitcoinPurpleTestnet(BitcoinPurple):

    NET_NAME = "testnet"
    TESTNET = True

    # Testnet uses the same address/WIF prefixes as mainnet (see chainparams)
    WIF_PREFIX = 0xb7           # chainparams.cpp:266
    ADDRTYPE_P2PKH = 56         # chainparams.cpp:264
    ADDRTYPE_P2SH = 55          # chainparams.cpp:265
    SEGWIT_HRP = "tbtcp"        # chainparams.cpp:270
    BOLT11_HRP = SEGWIT_HRP

    GENESIS = "000002fdc3921c1ad368816fcc587f499698d42b42ab5a5d94ee67882ef9d998"
    DEFAULT_PORTS = {'t': '60001', 's': '60002'}
    BIP44_COIN_TYPE = 1         # standard testnet coin type
    LN_REALM_BYTE = 1

    # SLIP-0132 — standard Bitcoin testnet values (BIP32 root: 043587CF / 04358394)
    XPRV_HEADERS = {
        'standard':    0x04358394,  # tprv
        'p2wpkh-p2sh': 0x044a4e28,  # uprv
        'p2wsh-p2sh':  0x024285b5,  # Uprv
        'p2wpkh':      0x045f18bc,  # vprv
        'p2wsh':       0x02575048,  # Vprv
    }
    XPRV_HEADERS_INV = inv_dict(XPRV_HEADERS)
    XPUB_HEADERS = {
        'standard':    0x043587cf,  # tpub
        'p2wpkh-p2sh': 0x044a5262,  # upub
        'p2wsh-p2sh':  0x024289ef,  # Upub
        'p2wpkh':      0x045f1cf6,  # vpub
        'p2wsh':       0x02575483,  # Vpub
    }
    XPUB_HEADERS_INV = inv_dict(XPUB_HEADERS)
```

### 7.3 Derivation Paths (BIP44 / 49 / 84 / 86)

Standard HD paths for each script type. Replace `COIN_TYPE` with the registered
value (TBD — see §7.1 note).

| BIP | Script type | Path template | xpub/xprv prefix |
|-----|-------------|---------------|-----------------|
| BIP44 | P2PKH (legacy) | `m/44'/COIN_TYPE'/0'/0/n` | `xpub` / `xprv` |
| BIP49 | P2WPKH-P2SH (wrapped SegWit) | `m/49'/COIN_TYPE'/0'/0/n` | `ypub` / `yprv` |
| BIP84 | P2WPKH (native SegWit) | `m/84'/COIN_TYPE'/0'/0/n` | `zpub` / `zprv` |
| BIP86 | P2TR (Taproot) | `m/86'/COIN_TYPE'/0'/0/n` | `xpub` / `xprv` or descriptors |

- `ACCOUNT` = `0'` (first account, hardened)
- `CHANGE` = `0` (receive) or `1` (change)
- `INDEX` = address index (unhardened)

### 7.4 Checkpoints (`checkpoints.json`)

Electrum uses checkpoints for SPV header chain verification.
The file lives at `electrum/chains/bitcoinpurple/checkpoints.json`.

Format: a JSON array of `[header_hash_hex, accumulated_work_int]` pairs,
one entry per 2016-block chunk. Chunk `n` covers blocks `n*2016` to `(n+1)*2016-1`.

```json
[
  [
    "000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015",
    1048592
  ]
]
```

The first entry (chunk 0) is the genesis block hash with its accumulated PoW work
(`0x00000000000000000000000000000000000000000000074e7000dc41ac550926` — from `nMinimumChainWork` in chainparams.cpp:104, updated at block 1,048,808).

**To generate a full checkpoints.json** from a running node:

```python
import json, subprocess, math

def get_header(height):
    h = subprocess.check_output(
        ['bitcoinpurple-cli', 'getblockhash', str(height)]).decode().strip()
    return subprocess.check_output(
        ['bitcoinpurple-cli', 'getblockheader', h, 'true']).decode()

checkpoints = []
tip = int(subprocess.check_output(
    ['bitcoinpurple-cli', 'getblockcount']).decode().strip())

for chunk in range(tip // 2016 + 1):
    height = chunk * 2016
    import json as _j
    header = _j.loads(get_header(height))
    checkpoints.append([header['hash'], int(header['chainwork'], 16)])

print(json.dumps(checkpoints, indent=2))
```

### 7.5 `servers.json` Format

Place at `electrum/chains/bitcoinpurple/servers.json` (mainnet)
and `electrum/chains/testnet/servers.json` (testnet).

```json
{
  "your-server.example.com": {
    "pruning": "-",
    "s": "50002",
    "t": "50001",
    "version": "1.4.2"
  }
}
```

| Field | Meaning |
|-------|---------|
| key | hostname or IP of the ElectrumX server |
| `"pruning"` | `"-"` = full node; a number = pruned at that height |
| `"s"` | SSL port |
| `"t"` | TCP plain port |
| `"version"` | minimum Electrum protocol version required |

### 7.6 Dust Thresholds

Minimum output values below which an output is considered "dust" and non-standard.
These are the same as Bitcoin since BTCP uses identical script formats.

| Script type | Dust limit | Policy fee rate |
|-------------|-----------|-----------------|
| P2PKH | 546 sat | `DUST_RELAY_TX_FEE` = 3000 sat/kvB (`src/policy/policy.h:55`) |
| P2WPKH (native SegWit) | 294 sat | same |
| P2WSH | 330 sat | same |
| P2TR (Taproot) | 294 sat | same |
| `OP_RETURN` | 0 (unspendable) | max 83 bytes (`src/script/standard.h:34`) |

### 7.7 Electrum Header Verification

Do not reuse Bitcoin's 2016-block difficulty verification logic unchanged.
BTCP uses Bitcoin-style compact targets and double-SHA256 proof-of-work, but
retargets every 120 blocks with a 7,200 second target timespan.

Wallet constants / chain-verifier values:

```python
POW_LIMIT = int(
    "00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16
)
TARGET_SPACING = 60
TARGET_TIMESPAN = 120 * 60
DIFFICULTY_ADJUSTMENT_INTERVAL = 120
MAX_ADJUSTMENT_FACTOR = 4
```

Header validation must perform:

1. Verify `double_sha256(header) <= target_from_nbits(header.bits)`.
2. Verify target is `> 0` and `<= POW_LIMIT`.
3. If `height % 120 != 0`, require `header.bits == previous.bits`.
4. If `height % 120 == 0`, compute expected `bits` from the previous 120-block
   window using the §2.7 formula.
5. Verify each header links to the previous header hash.
6. Use `GENESIS` to anchor the chain and `checkpoints.json` to accelerate SPV
   verification.

If the Electrum fork does not yet implement BTCP's 120-block retarget logic,
set `SKIP_POW_DIFFICULTY_VALIDATION = True` temporarily for development only.
Do not ship a production wallet with difficulty validation disabled.

### 7.8 Electrum Wallet Build Checklist

Files that must be added or changed in an Electrum fork:

| File / area | Required BTCP change |
|-------------|----------------------|
| `electrum/constants.py` | Add `BitcoinPurple` and `BitcoinPurpleTestnet` classes |
| `electrum/chains/bitcoinpurple/servers.json` | Add real ElectrumX host(s), ports `50001` / `50002` |
| `electrum/chains/bitcoinpurple/checkpoints.json` | Generate from a synced BTCP node |
| header chain verifier | Use 120-block retarget and BTCP `powLimit` |
| address module | Accept Base58 versions 56/55 and Bech32 HRP `btcp` |
| transaction/wallet formats | Use BTCP provisional BIP44 coin type consistently |
| Lightning invoice parser | Accept `lnbtcp` / `lntbtcp` BOLT11 prefixes if LN is enabled |
| UI/network selector | Expose BitcoinPurple mainnet/testnet names and datadirs |

---

## 8. Lightning Network

This section documents the chain-specific parameters required to build or fork
a Lightning Network implementation for BTCP. General BOLT protocol behaviour
(onion routing, payment flow, gossip) is identical to Bitcoin LN.

### 8.1 Chain Identification

In BOLT1, every message that references a specific chain carries a `chain_hash`.
This is the genesis block hash in **wire byte order** (i.e. the display hex reversed byte-by-byte).

| Network | Genesis hash (display) | chain_hash (BOLT1 wire) |
|---------|------------------------|-------------------------|
| Mainnet | `000003823fbf82ea…c015` | `15c04ef0bc1856d6b1ec199ca25d0aa7e77c6114e2cb0649ea82bf3f82030000` |
| Testnet | `000002fdc3921c1a…d998` | `98d9f92e8867ee945d5aab422bd49896497f58cc6f8168d31a1c92c3fd020000` |

The `chain_hash` appears in channel-establishment, channel-gossip, and gossip-query
messages such as `open_channel`, `accept_channel`, `funding_created`,
`channel_announcement`, `channel_update`, `query_channel_range`, and
`reply_channel_range`. BOLT11 invoices do not normally carry `chain_hash`; their
network is selected by the invoice HRP.

### 8.2 BOLT11 Invoice Prefix

| Network | HRP | Example invoice start |
|---------|-----|-----------------------|
| Mainnet | `btcp` | `lnbtcp1…` |
| Testnet | `tbtcp` | `lntbtcp1…` |

Amount suffix multipliers (same as Bitcoin):

| Multiplier | Value |
|------------|-------|
| `m` | 0.001 BTCP (100,000 sat) |
| `u` | 0.000001 BTCP (100 sat) |
| `n` | 0.000000001 BTCP (0.1 sat) |
| `p` | 0.000000000001 BTCP (0.0001 sat) |

### 8.3 Block-Time-Scaled Timeout Parameters

**This is the most critical section for LN on BTCP.**

BTCP has 1-minute blocks (vs Bitcoin's 10-minute blocks). All LN timeout parameters
expressed in blocks must be scaled by ×10 to achieve the same real-world security
windows as Bitcoin LN. Failure to do this results in dangerously short penalty and
payment expiry windows.

| Parameter | Source type | Bitcoin common default | BTCP recommended (1 min/block) | Real-world time |
|-----------|----------|------------------------|-------------------------------|-----------------|
| `to_self_delay` (justice window) | implementation policy | 144 blocks | **1440 blocks** | ~24 hours |
| `cltv_expiry_delta` per routing hop | implementation policy / BOLT7 field | 40 blocks | **400 blocks** | ~6.7 hours |
| `min_final_cltv_expiry_delta` (last hop) | implementation policy / BOLT11 field | 9 blocks | **90 blocks** | ~90 minutes |
| maximum remote `to_self_delay` accepted | BOLT2 policy limit | 2016 blocks | **20160 blocks** | ~14 days |
| `max_cltv_expiry` (max payment timeout) | implementation policy | 2016 blocks | **20160 blocks** | ~14 days |
| Channel funding confirmation target | best practice | 3–6 blocks | **30–60 blocks** | ~30–60 minutes |

> **Why this matters:** if a remote party broadcasts a revoked commitment transaction,
> your node has until `to_self_delay` blocks to publish the penalty transaction.
> With 1-min blocks and Bitcoin's default of 144, you would have only 2.4 hours.
> Using the recommended 1440 gives a full 24 hours — the same window as Bitcoin.

### 8.4 Channel Parameters

These match Bitcoin LN defaults and do not need to change for BTCP.

| Parameter | Value | Note |
|-----------|-------|------|
| `dust_limit_satoshis` | 354 sat (P2WPKH anchor) or 546 sat (legacy) | minimum output in commitment tx |
| `max_htlc_value_in_flight_msat` | 0 (unlimited) or % of capacity | channel-operator choice |
| `max_accepted_htlcs` | 483 | BOLT3 protocol maximum (script complexity limit) |
| `htlc_minimum_msat` | 1 msat | minimum HTLC size |
| `channel_reserve_satoshis` | ~1% of channel capacity (min 1000 sat) | reserves the counterparty cannot spend |
| `fee_base_msat` | 1000 (1 sat) | routing fee base |
| `fee_proportional_millionths` | 1 (0.0001%) | routing fee rate |
| `feerate_per_kw` | node-determined | initial commitment transaction fee rate |

### 8.5 Feature Bits (BOLT1 `init`)

LN feature bits are chain-agnostic; BTCP uses the same bit assignments as Bitcoin LN.

| Feature | Bit pair | Status |
|---------|----------|--------|
| `var_onion_optin` | 8/9 | mandatory |
| `option_static_remotekey` | 12/13 | mandatory |
| `payment_secret` | 14/15 | mandatory |
| `basic_mpp` (multi-part payments) | 16/17 | optional |
| `option_anchors_zero_fee_htlc_tx` | 22/23 | optional (preferred over legacy anchors) |
| `option_scid_alias` | 46/47 | optional |
| `option_zero_conf` | 50/51 | optional |

### 8.6 Shared Implementation Fork Notes

All major LN implementations (LND, CLN, Eclair, LDK) hardcode Bitcoin's chain hash.
Forking any of them for BTCP requires at minimum:

1. Replace the genesis hash / chain_hash constant with the BTCP value (§8.1)
2. Replace the BOLT11 invoice HRP with `btcp` (§8.2)
3. Update all block-count-based timeout defaults (§8.3)
4. Point the Bitcoin RPC backend to `bitcoinpurpled` on port `13495`
5. Update the network / bech32 address validation to accept `btcp1…` addresses

Also update any constants derived from Bitcoin's 10-minute block cadence:
confirmation targets, fee-estimation targets, CLTV deltas, wallet rescan
lookbacks, channel announcement depth policy, and watchtower/penalty windows.

### 8.7 Core Lightning (CLN) Fork Parameters

Core Lightning is Bitcoin-specific upstream. A BTCP fork needs a new chain
definition or equivalent patches wherever CLN selects `bitcoin`, `testnet`,
`signet`, or `regtest`.

| Area | BTCP mainnet value / action |
|------|-----------------------------|
| Network name | add `bitcoinpurple` / `btcp` network selector |
| Chain hash | `15c04ef0bc1856d6b1ec199ca25d0aa7e77c6114e2cb0649ea82bf3f82030000` |
| On-chain RPC backend | `bitcoinpurple-cli` / `bitcoinpurpled` RPC on `127.0.0.1:13495` |
| Bech32 address HRP | `btcp` |
| BOLT11 HRP | `btcp` (`lnbtcp...`) |
| Native unit | 1 BTCP = 100,000,000 sat; 1 sat = 1,000 msat |
| Genesis display hash | `000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015` |
| P2P gossip chain filter | accept only BTCP `chain_hash` |
| Fee estimates | call BTCP daemon `estimatesmartfee`; scale targets for 1-minute blocks |
| Confirmation policy | use 30-60 blocks where you want Bitcoin-like 30-60 minute confidence |
| Timeout defaults | use §8.3 scaled block counts |
| DNS bootstrap | empty until BTCP LN seed infrastructure exists |

CLN does not require Bitcoin Core ZMQ or `txindex=1` for normal operation; it
polls the backend over RPC. If CLN and ElectrumX share one `bitcoinpurpled`,
increase `rpcworkqueue` and monitor RPC latency.

### 8.8 LND Fork Parameters

LND uses btcsuite chain parameters and Bitcoin-specific network selection. A BTCP
fork needs equivalent new `chaincfg` / chain registry parameters.

| Area | BTCP mainnet value / action |
|------|-----------------------------|
| Chain registry | add BitcoinPurple params instead of `chaincfg.MainNetParams` |
| RPC backend | `bitcoind`-style backend pointed to `bitcoinpurpled:13495` |
| ZMQ raw block | `bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332` if using ZMQ |
| ZMQ raw tx | `bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333` if using ZMQ |
| Address params | P2PKH 56, P2SH 55, Bech32 `btcp`, WIF 183 |
| Chain hash | same §8.1 wire value |
| Invoice HRP | `btcp` |
| Coin type | use the same provisional Electrum value until SLIP-0044 registration |
| Timeout defaults | use §8.3 scaled block counts |
| Fee estimator | ensure targets are interpreted as 1-minute BTCP blocks |

Unlike ElectrumX, LND normally benefits from ZMQ for prompt block/transaction
notifications. If ZMQ is omitted, use the implementation's RPC polling mode and
expect higher latency.

### 8.9 Lightning Difficulty / Block Cadence Implications

LN implementations do not recalculate proof-of-work difficulty themselves for
normal operation; the full node validates blocks. The LN daemon consumes validated
block headers/blocks from `bitcoinpurpled` and uses block heights for timeouts.

What must still be changed in LN code:

- Treat one BTCP block as ~60 seconds when converting user-facing time windows to
  block counts.
- Use BTCP's `chain_hash` everywhere gossip or channel messages identify a chain.
- Use BTCP's address and BOLT11 HRPs for invoices, fallback addresses, and
  on-chain outputs.
- Do not connect to Bitcoin LN peers or DNS seeds; BTCP LN needs its own network
  graph and bootstrap peers.

---

## 9. `bitcoinpurple.conf` Reference

### 9.1 Default Values

| Parameter | Default | Source |
|-----------|---------|--------|
| `dbcache` | 450 MiB | `src/txdb.h:30` |
| `maxmempool` | 300 MB | `src/kernel/mempool_options.h:20` |
| `mempoolexpiry` | 336 h (14 days) | `src/kernel/mempool_options.h:24` |
| `blockmaxweight` | 3,996,000 wu | `src/policy/policy.h:23` |
| `rpcthreads` | 4 | `src/httpserver.h:12` |
| `rpcworkqueue` | 16 | `src/httpserver.h:13` |
| `rpcservertimeout` | 30 s | `src/httpserver.h:14` |
| `maxconnections` | 125 | `src/net.h` |

### 9.2 Full Annotated Config

```ini
##############################################################################
# bitcoinpurple.conf — full node + solo mining + ElectrumX backend
# Location: ~/.bitcoinpurple/bitcoinpurple.conf
##############################################################################

# ── Network ──────────────────────────────────────────────────────────────────
# mainnet by default; uncomment for testnet
#testnet=1

listen=1
maxconnections=125
# addnode=node3.walletbuilders.com

# ── Chain & Indexes ───────────────────────────────────────────────────────────
# txindex=1 is REQUIRED by ElectrumX — incompatible with prune
txindex=1
# blockfilterindex=1  # optional: BIP157/158 compact filters for light clients
# prune=0             # never prune when txindex=1

# ── Performance ───────────────────────────────────────────────────────────────
dbcache=450        # MiB (default: 450; raise on high-RAM machines)
maxmempool=300     # MB (default: 300)
mempoolexpiry=336  # hours before unconfirmed txs are evicted (default: 336 = 14 days)

# ── RPC Server (required by ElectrumX) ───────────────────────────────────────
server=1
rpcport=13495
rpcbind=127.0.0.1
rpcallowip=127.0.0.1      # set to container subnet when ElectrumX is in Docker
rpcuser=btcpuser
rpcpassword=CHANGE_ME_USE_STRONG_PASSWORD
rpcthreads=4
rpcworkqueue=64           # raised from default 16 for ElectrumX parallel RPC calls
rpcservertimeout=30

# ── ZMQ Notifications (optional real-time updates) ───────────────────────────
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
zmqpubhashblock=tcp://127.0.0.1:28334
zmqpubhashtx=tcp://127.0.0.1:28335
zmqpubrawblockhwm=500
zmqpubrawtxhwm=500
zmqpubhashblockhwm=500
zmqpubhashtxhwm=500

# ── Mining ────────────────────────────────────────────────────────────────────
# MAX_BLOCK_WEIGHT = 4,000,000 wu  (consensus/consensus.h:15)
blockmaxweight=3996000
blockmintxfee=0.00001
# blocknotify=/usr/local/bin/notify_new_block.sh %s

# ── Wallet (disable if mining to an external address via getblocktemplate) ───
# disablewallet=1
```

### 9.3 Notes

- **`txindex=1` and `prune` are mutually exclusive.** ElectrumX requires `txindex=1`.
- **ZMQ** requires `--enable-zmq` at build time. Verify: `bitcoinpurple-cli getnetworkinfo | grep zmq`. ElectrumX can index through RPC polling; LND-style backends usually use ZMQ for low-latency block/tx notifications.
- **Solo mining** via `getblocktemplate` (BIP22): point your miner to `http://btcpuser:CHANGE_ME@127.0.0.1:13495`.
- **Docker networking:** set `rpcallowip` to the container subnet (e.g. `172.17.0.0/16`) when ElectrumX runs in a separate container.
- **LN node:** the LN daemon also connects to `bitcoinpurpled` via RPC. Set `rpcworkqueue` high enough (128+) if both ElectrumX and an LN node share the same node instance.

### 9.4 Minimal ElectrumX `env` (standalone / non-Docker)

```env
COIN=BitcoinPurple
NET=mainnet
DAEMON_URL=http://btcpuser:CHANGE_ME@127.0.0.1:13495/
DB_DIRECTORY=/data/electrumx
SERVICES=tcp://0.0.0.0:50001,ssl://0.0.0.0:50002,rpc://0.0.0.0:8000
REPORT_SERVICES=tcp://YOUR_PUBLIC_IP:50001,ssl://YOUR_PUBLIC_IP:50002
SSL_CERTFILE=/certs/server.crt
SSL_KEYFILE=/certs/server.key
CACHE_MB=1200
MAX_SESSIONS=1000
INITIAL_CONCURRENT=2
COST_SOFT_LIMIT=0
COST_HARD_LIMIT=0
PEER_DISCOVERY=on
PEER_ANNOUNCE=true
```
