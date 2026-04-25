"""
Integration tests: web dashboard against real backends.
Requires stack to be up (docker compose up -d).
"""

import pytest
import requests

BASE = 'http://localhost:8080'
TIMEOUT = 10


@pytest.mark.integration
def test_health_both_services_up():
    """Both services must report 'up', not just that the endpoint returns 200."""
    r = requests.get(f'{BASE}/api/health', timeout=TIMEOUT)
    assert r.status_code == 200
    data = r.json()
    assert data.get('status') == 'healthy', (
        f"Stack is not fully healthy: {data.get('services')}"
    )
    assert data['services']['bitcoinpurple'] == 'up', 'Node is down'
    assert data['services']['electrumx'] == 'up', 'ElectrumX is down'


@pytest.mark.integration
def test_block_height_syncing():
    """Node must report a block height — and the key must actually be present."""
    r = requests.get(f'{BASE}/api/bitcoinpurple/block-height', timeout=TIMEOUT)
    assert r.status_code == 200
    data = r.json()
    assert 'block_height' in data, f'Missing block_height in response: {data}'
    assert data['block_height'] > 0, f'Block height is {data["block_height"]}, node may not be syncing'


@pytest.mark.integration
def test_node_has_peers():
    """Node must have at least one P2P peer — otherwise it cannot sync."""
    r = requests.get(f'{BASE}/api/bitcoinpurple/peers', timeout=TIMEOUT)
    assert r.status_code == 200
    data = r.json()
    total = data.get('total', 0)
    assert total > 0, f'Node has no peers connected (total={total}) — check P2P port and network'


@pytest.mark.integration
def test_node_headers_match_blocks():
    """headers == blocks means the node is fully synced (not just started)."""
    r = requests.get(f'{BASE}/api/bitcoinpurple/info', timeout=TIMEOUT)
    assert r.status_code == 200
    blockchain = r.json().get('blockchain', {})
    blocks = blockchain.get('blocks', -1)
    headers = blockchain.get('headers', -2)
    assert blocks >= 0, 'Cannot read blocks from node'
    assert blocks == headers, (
        f'Node is still syncing: blocks={blocks}, headers={headers}'
    )


@pytest.mark.integration
def test_system_resources_in_valid_range():
    """CPU/memory/disk percent must be in [0, 100] — not just non-negative."""
    r = requests.get(f'{BASE}/api/system/resources', timeout=TIMEOUT)
    assert r.status_code == 200
    data = r.json()
    for resource in ('cpu', 'memory', 'disk'):
        pct = data[resource]['percent']
        assert isinstance(pct, (int, float)), f'{resource}.percent is not a number: {pct}'
        assert 0 <= pct <= 100, f'{resource}.percent out of range: {pct}'


@pytest.mark.integration
def test_electrumx_stats_have_version():
    """ElectrumX stats must contain a real server_version, not Unknown or empty."""
    r = requests.get(f'{BASE}/api/electrumx/stats', timeout=TIMEOUT)
    assert r.status_code == 200
    stats = r.json().get('stats', {})
    version = stats.get('server_version', '')
    assert version and version not in ('Unknown', ''), (
        f'ElectrumX server_version is missing or unknown: {version!r}'
    )
