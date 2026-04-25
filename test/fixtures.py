"""Shared test data used by unit tests."""

MOCK_RPC_DATA = {
    'getblockchaininfo': {
        'chain': 'main', 'blocks': 100_000, 'headers': 100_000,
        'difficulty': 1_234_567.89, 'bestblockhash': 'ab' * 32,
    },
    'getnetworkinfo': {'version': 110_100, 'subversion': '/BitcoinPurple:1.1.1/', 'connections': 8},
    'getmininginfo': {'networkhashps': 9_876_543_210.0, 'difficulty': 1_234_567.89},
    'getpeerinfo': [{'addr': '1.2.3.4:13496', 'inbound': False,
                     'subver': '/BitcoinPurple:1.1.1/', 'conntime': 1_000,
                     'bytessent': 512, 'bytesrecv': 1_024}],
    'getmempoolinfo': {'size': 0, 'bytes': 0},
    'getblockcount': 100_000,
    'getnetworkhashps': 9_876_543_210.0,
    'getdifficulty': 1_234_567.89,
    'getblocksubsidy': {'miner': 50.0, 'masternode': 0.0},
    'getblockhash': 'deadbeef' * 8,
    'getblock': {'height': 100_000, 'hash': 'deadbeef' * 8, 'time': 1_700_000_000,
                 'size': 300, 'tx': ['tx1']},
}

MOCK_ELECTRUMX_STATS = {
    'server_version': 'ElectrumX 1.16.0',
    'protocol_min': '1.4',
    'protocol_max': '1.4.2',
    'genesis_hash': '000003823fbf82ea...',
    'genesis_hash_full': '000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015',
    'hash_function': 'sha256d',
    'pruning': None,
    'sessions': 3,
    'peer_discovery': 'on',
    'peer_announce': 'on',
    'active_servers': [{'host': '1.2.3.4', 'tcp_port': '51001', 'ssl_port': '51002',
                        'tcp_reachable': True, 'ssl_reachable': True}],
    'active_servers_count': 1,
    'requests': 0,
    'subs': 0,
    'uptime': 3_600,
    'db_size': 1_073_741_824,
    'tcp_port': '51001',
    'ssl_port': '51002',
    'server_ip': '5.6.7.8',
}


def local_env():
    return {'environ_base': {'REMOTE_ADDR': '127.0.0.1'}}


def external_env(**extra_headers):
    return {'environ_base': {'REMOTE_ADDR': '8.8.8.8'}, 'headers': extra_headers}
