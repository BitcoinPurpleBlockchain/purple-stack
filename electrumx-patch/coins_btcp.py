from electrumx.lib.coins import Bitcoin
from electrumx.lib import tx as lib_tx

class BitcoinPurple(Bitcoin):
    NAME = "BitcoinPurple"
    SHORTNAME = "BTCP"
    NET = "mainnet"

    # === Prefix address (from bitcoinpurplecore/src/kernel/chainparams.cpp) ===
    P2PKH_VERBYTE = bytes([0x38])   # 56 decimal
    P2SH_VERBYTE  = bytes([0x37])   # 55 decimal
    WIF_BYTE      = bytes([0xb7])   # 183 decimal

    # === bech32 prefix ===
    HRP = "btcp"

    # === Genesis hash ===
    GENESIS_HASH = "000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015"

    # === Clear inherited Bitcoin checkpoints ===
    CHECKPOINTS = []

    # === Network statistics (required by ElectrumX) ===
    TX_COUNT = 1039113
    TX_COUNT_HEIGHT = 917081
    TX_PER_BLOCK = 2

    # === Default ports ===
    RPC_PORT = 13495
    PEER_DEFAULT_PORTS = {'t': '60001', 's': '60002'}

    # === Seed peers for discovery ===
    PEERS = [
        'node3.walletbuilders.com t s',
    ]

    # === Deserializer ===
    DESERIALIZER = lib_tx.DeserializerSegWit


class BitcoinPurpleTestnet(BitcoinPurple):
    NAME = "BitcoinPurple"
    SHORTNAME = "tBTCP"
    NET = "testnet"

    # === Testnet bech32 prefix ===
    HRP = "tbtcp"

    # === Testnet genesis hash ===
    GENESIS_HASH = "000002fdc3921c1ad368816fcc587f499698d42b42ab5a5d94ee67882ef9d998"

    # === Network statistics ===
    TX_COUNT = 500
    TX_COUNT_HEIGHT = 1
    TX_PER_BLOCK = 2

    # === Testnet ports ===
    RPC_PORT = 23495
    PEER_DEFAULT_PORTS = {'t': '70001', 's': '70002'}
    PEERS = []
