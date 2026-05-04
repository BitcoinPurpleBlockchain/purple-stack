# coins_btcp.py — BitcoinPurple (BTCP) coin definitions for ElectrumX
# Patch into electrumx/lib/coins.py alongside the Bitcoin class.
# Source: technical-data.md / src/kernel/chainparams.cpp

from electrumx.lib.coins import Bitcoin
from electrumx.lib import tx as lib_tx


class BitcoinPurple(Bitcoin):
    NAME = 'BitcoinPurple'
    SHORTNAME = 'BTCP'
    NET = 'mainnet'

    # Genesis block — completely different from Bitcoin; clear inherited checkpoints
    GENESIS_HASH = (
        '000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015'
    )
    CHECKPOINTS = {}  # Bitcoin checkpoints would fail against this genesis

    # Base58 address prefixes (src/kernel/chainparams.cpp:154-156)
    P2PKH_VERBYTE = bytes([56])        # 0x38 — mainnet P2PKH addresses start with 'P'
    P2SH_VERBYTES = (bytes([55]),)     # 0x37 — mainnet P2SH addresses start with 'P'
    WIF_BYTE      = bytes([183])       # 0xb7

    # BIP32 HD key version bytes (src/kernel/chainparams.cpp:157-158)
    XPUB_VERBYTES = bytes.fromhex('0488B21E')   # xpub
    XPRV_VERBYTES = bytes.fromhex('0488ADE4')   # xprv

    # Bech32 / SegWit HRP (src/kernel/chainparams.cpp:160) — addresses start with btcp1…
    SEGWIT_HRP = 'btcp'

    # SegWit active from genesis (BIP141/143/147 height 0); Taproot ALWAYS_ACTIVE
    DESERIALIZER = lib_tx.DeserializerSegWit

    # Do not inherit Bitcoin peers or version gates.
    PEERS = [
        '173.212.224.67 t51001 s51002',
        '144.91.120.225 t51001 s51002',
        '66.94.115.80 t51001 s51002',
        '89.117.149.130 t51001 s51002',
        '84.247.169.248 t51001 s51002',
    ]
    MIN_REQUIRED_DAEMON_VERSION = '1.1.1'
    BLACKLIST_URL = None

    # 1-minute blocks: keep enough undo data for practical reorg handling (×10 vs Bitcoin).
    REORG_LIMIT = 1200

    # Chain stats — overwritten at ElectrumX startup via getchaintxstats RPC
    # (src/kernel/chainparams.cpp:178-184); updated at block 1,048,808 (Apr 2026)
    TX_COUNT        = 1_189_400
    TX_COUNT_HEIGHT = 1_048_808
    TX_PER_BLOCK    = 2

    # Node RPC port — mainnet (src/chainparamsbase.cpp:47)
    RPC_PORT = 13495

    # Default Electrum peer ports
    PEER_DEFAULT_PORTS = {'t': '50001', 's': '50002'}


class BitcoinPurpleTestnet(BitcoinPurple):
    NAME     = 'BitcoinPurple Testnet'
    SHORTNAME = 'TBTCP'
    NET       = 'testnet'

    # Testnet genesis (src/kernel/chainparams.cpp:259)
    GENESIS_HASH = (
        '000002fdc3921c1ad368816fcc587f499698d42b42ab5a5d94ee67882ef9d998'
    )
    CHECKPOINTS = {}

    # Testnet BIP32 HD key version bytes (src/kernel/chainparams.cpp:267-268)
    XPUB_VERBYTES = bytes.fromhex('043587CF')
    XPRV_VERBYTES = bytes.fromhex('04358394')

    # Bech32 HRP for testnet (src/kernel/chainparams.cpp:270)
    SEGWIT_HRP = 'tbtcp'

    TX_COUNT        = 1
    TX_COUNT_HEIGHT = 0
    TX_PER_BLOCK    = 1

    # Testnet RPC port (src/chainparamsbase.cpp:49)
    RPC_PORT = 23495

    PEERS = []
    REORG_LIMIT = 1200
    PEER_DEFAULT_PORTS = {'t': '60001', 's': '60002'}
