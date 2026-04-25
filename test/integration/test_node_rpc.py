"""
Integration tests: BitcoinPurple node RPC.
Requires stack to be up (docker compose up -d).

RPC port 13495 is internal to the Docker network (not exposed on the host).
Tests run via `docker exec bitcoinpurple-node bitcoinpurple-cli ...`.
"""

import json
import socket
import subprocess
import os
import pytest

MAINNET_GENESIS = '000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015'
P2P_PORT = 13496


def _read_rpc_credentials():
    conf = os.path.join(os.path.dirname(__file__), '..', '..', '.bitcoinpurple', 'bitcoinpurple.conf')
    user = password = None
    with open(conf) as f:
        for line in f:
            line = line.strip()
            if line.startswith('rpcuser='):
                user = line.split('=', 1)[1]
            elif line.startswith('rpcpassword='):
                password = line.split('=', 1)[1]
    return user, password


def _cli(*args):
    """Run bitcoinpurple-cli inside the node container and return parsed JSON output."""
    user, password = _read_rpc_credentials()
    result = subprocess.run(
        [
            'docker', 'exec', 'bitcoinpurple-node',
            'bitcoinpurple-cli',
            f'-rpcuser={user}',
            f'-rpcpassword={password}',
            *args,
        ],
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        pytest.fail(f'bitcoinpurple-cli {args[0]} failed:\n{result.stderr}')
    text = result.stdout.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


@pytest.mark.integration
def test_getblockchaininfo_chain():
    info = _cli('getblockchaininfo')
    assert info['chain'] == 'main'


@pytest.mark.integration
def test_block_height_positive():
    info = _cli('getblockchaininfo')
    assert info['blocks'] > 0


@pytest.mark.integration
def test_genesis_hash_matches():
    genesis = _cli('getblockhash', '0')
    # CLI returns a plain string (no quotes in JSON scalar)
    assert genesis.strip('"') == MAINNET_GENESIS or genesis == MAINNET_GENESIS


@pytest.mark.integration
def test_p2p_port_open():
    try:
        s = socket.create_connection(('localhost', P2P_PORT), timeout=3)
        s.close()
    except OSError as e:
        pytest.fail(f'P2P port {P2P_PORT} not reachable: {e}')
