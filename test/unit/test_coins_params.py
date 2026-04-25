"""
Validate BitcoinPurple coin parameters against technical-data.md values.
These tests catch silent misconfiguration in electrumx-patch/coins_btcp.py.
"""

import importlib.util
import os
import sys
import pytest

# Load coins_btcp.py without requiring a full ElectrumX install by stubbing
# the two imports it needs.
_COINS_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'electrumx-patch', 'coins_btcp.py'
)


def _load_coins():
    """Import coins_btcp with minimal stubs for electrumx dependencies."""
    # Stub electrumx.lib.coins.Bitcoin
    import types

    electrumx_pkg = types.ModuleType('electrumx')
    electrumx_lib = types.ModuleType('electrumx.lib')
    electrumx_coins = types.ModuleType('electrumx.lib.coins')
    electrumx_tx = types.ModuleType('electrumx.lib.tx')

    class _Bitcoin:
        pass

    class _DeserializerSegWit:
        pass

    electrumx_coins.Bitcoin = _Bitcoin
    electrumx_tx.DeserializerSegWit = _DeserializerSegWit

    sys.modules.setdefault('electrumx', electrumx_pkg)
    sys.modules.setdefault('electrumx.lib', electrumx_lib)
    sys.modules.setdefault('electrumx.lib.coins', electrumx_coins)
    sys.modules.setdefault('electrumx.lib.tx', electrumx_tx)

    spec = importlib.util.spec_from_file_location('coins_btcp', _COINS_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_coins = _load_coins()
BitcoinPurple = _coins.BitcoinPurple
BitcoinPurpleTestnet = _coins.BitcoinPurpleTestnet


# ── Mainnet ──────────────────────────────────────────────────────────────────

class TestBitcoinPurpleMainnet:
    def test_name(self):
        assert BitcoinPurple.NAME == 'BitcoinPurple'

    def test_shortname(self):
        assert BitcoinPurple.SHORTNAME == 'BTCP'

    def test_net(self):
        assert BitcoinPurple.NET == 'mainnet'

    def test_genesis_hash(self):
        assert BitcoinPurple.GENESIS_HASH == (
            '000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015'
        )

    def test_genesis_hash_length(self):
        assert len(BitcoinPurple.GENESIS_HASH) == 64

    def test_checkpoints_empty(self):
        assert BitcoinPurple.CHECKPOINTS == {}

    def test_p2pkh_verbyte(self):
        # src/kernel/chainparams.cpp:154 — 0x38 = 56
        assert BitcoinPurple.P2PKH_VERBYTE == bytes([56])

    def test_p2sh_verbytes(self):
        # src/kernel/chainparams.cpp:155 — 0x37 = 55
        assert BitcoinPurple.P2SH_VERBYTES == (bytes([55]),)

    def test_wif_byte(self):
        # src/kernel/chainparams.cpp:156 — 0xb7 = 183
        assert BitcoinPurple.WIF_BYTE == bytes([183])

    def test_xpub_verbytes(self):
        assert BitcoinPurple.XPUB_VERBYTES == bytes.fromhex('0488B21E')

    def test_xprv_verbytes(self):
        assert BitcoinPurple.XPRV_VERBYTES == bytes.fromhex('0488ADE4')

    def test_segwit_hrp(self):
        assert BitcoinPurple.SEGWIT_HRP == 'btcp'

    def test_rpc_port(self):
        assert BitcoinPurple.RPC_PORT == 13495

    def test_reorg_limit(self):
        # 1-minute blocks → 1200 (×10 vs Bitcoin's 120)
        assert BitcoinPurple.REORG_LIMIT == 1200

    def test_peer_default_ports(self):
        assert BitcoinPurple.PEER_DEFAULT_PORTS == {'t': '51001', 's': '51002'}

    def test_tx_per_block_positive(self):
        assert BitcoinPurple.TX_PER_BLOCK >= 1

    def test_tx_count_positive(self):
        assert BitcoinPurple.TX_COUNT > 0

    def test_tx_count_height_positive(self):
        assert BitcoinPurple.TX_COUNT_HEIGHT > 0

    def test_blacklist_url_none(self):
        assert BitcoinPurple.BLACKLIST_URL is None

    def test_min_daemon_version(self):
        assert BitcoinPurple.MIN_REQUIRED_DAEMON_VERSION == '1.1.1'

    def test_peers_is_list(self):
        assert isinstance(BitcoinPurple.PEERS, list)

    def test_deserializer_is_segwit(self):
        from electrumx.lib.tx import DeserializerSegWit
        assert BitcoinPurple.DESERIALIZER is DeserializerSegWit


# ── Testnet ───────────────────────────────────────────────────────────────────

class TestBitcoinPurpleTestnet:
    def test_inherits_from_mainnet(self):
        assert issubclass(BitcoinPurpleTestnet, BitcoinPurple)

    def test_net(self):
        assert BitcoinPurpleTestnet.NET == 'testnet'

    def test_shortname(self):
        assert BitcoinPurpleTestnet.SHORTNAME == 'TBTCP'

    def test_genesis_hash(self):
        assert BitcoinPurpleTestnet.GENESIS_HASH == (
            '000002fdc3921c1ad368816fcc587f499698d42b42ab5a5d94ee67882ef9d998'
        )

    def test_genesis_hash_length(self):
        assert len(BitcoinPurpleTestnet.GENESIS_HASH) == 64

    def test_genesis_differs_from_mainnet(self):
        assert BitcoinPurpleTestnet.GENESIS_HASH != BitcoinPurple.GENESIS_HASH

    def test_segwit_hrp(self):
        assert BitcoinPurpleTestnet.SEGWIT_HRP == 'tbtcp'

    def test_rpc_port(self):
        assert BitcoinPurpleTestnet.RPC_PORT == 23495

    def test_xpub_verbytes(self):
        assert BitcoinPurpleTestnet.XPUB_VERBYTES == bytes.fromhex('043587CF')

    def test_xprv_verbytes(self):
        assert BitcoinPurpleTestnet.XPRV_VERBYTES == bytes.fromhex('04358394')

    def test_peers_empty(self):
        assert BitcoinPurpleTestnet.PEERS == []

    def test_checkpoints_empty(self):
        assert BitcoinPurpleTestnet.CHECKPOINTS == {}
