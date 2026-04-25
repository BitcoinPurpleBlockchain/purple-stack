"""
Tests for all /api/* endpoints in web-dashboard/app.py.

Covers:
- JSON response structure for every endpoint (mocked backends)
- Cache-Control headers
- Graceful error handling when RPC or ElectrumX is unavailable
"""

import pytest
from unittest.mock import patch

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fixtures import MOCK_RPC_DATA, MOCK_ELECTRUMX_STATS, local_env, external_env

API_KEY = 'test-api-key-for-pytest'


def _rpc_dispatch(method, params=None):
    return MOCK_RPC_DATA.get(method)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get(client, path):
    return client.get(path, **local_env())


# ── /api/health ───────────────────────────────────────────────────────────────

class TestHealth:
    @patch('app.get_electrumx_stats_cached', return_value=MOCK_ELECTRUMX_STATS)
    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_structure(self, _rpc, _ex, client):
        r = get(client, '/api/health')
        assert r.status_code == 200
        data = r.get_json()
        assert 'status' in data
        assert 'services' in data
        assert 'bitcoinpurple' in data['services']
        assert 'electrumx' in data['services']
        assert 'timestamp' in data

    @patch('app.get_electrumx_stats_cached', return_value=MOCK_ELECTRUMX_STATS)
    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_healthy_when_both_up(self, _rpc, _ex, client):
        r = get(client, '/api/health')
        data = r.get_json()
        assert data['status'] == 'healthy'
        assert data['services']['bitcoinpurple'] == 'up'
        assert data['services']['electrumx'] == 'up'

    @patch('app.get_electrumx_stats_cached', return_value=None)
    @patch('app.bitcoinpurple_rpc_call', return_value=None)
    def test_degraded_when_both_down(self, _rpc, _ex, client):
        r = get(client, '/api/health')
        assert r.status_code == 200
        data = r.get_json()
        assert data['status'] == 'degraded'
        assert data['services']['bitcoinpurple'] == 'down'
        assert data['services']['electrumx'] == 'down'


# ── /api/bitcoinpurple/info ───────────────────────────────────────────────────

class TestBitcoinPurpleInfo:
    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_structure(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/info')
        assert r.status_code == 200
        data = r.get_json()
        assert 'blockchain' in data
        assert 'network' in data
        assert 'mining' in data
        assert 'peers' in data
        assert 'mempool' in data
        assert 'timestamp' in data

    @patch('app.bitcoinpurple_rpc_call', return_value=None)
    def test_rpc_down_returns_valid_json(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/info')
        assert r.status_code == 200
        data = r.get_json()
        # Should return empty dicts, not crash
        assert 'blockchain' in data
        assert data['blockchain'] == {}


# ── /api/bitcoinpurple/block-height ──────────────────────────────────────────

class TestBlockHeight:
    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_structure(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/block-height')
        assert r.status_code == 200
        data = r.get_json()
        assert data.get('block_height') == 100_000
        assert 'timestamp' in data

    @patch('app.bitcoinpurple_rpc_call', return_value=None)
    def test_rpc_down_returns_error(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/block-height')
        assert r.status_code >= 400
        assert 'error' in r.get_json()


# ── /api/bitcoinpurple/network-hashrate ──────────────────────────────────────

class TestNetworkHashrate:
    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_structure(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/network-hashrate')
        assert r.status_code == 200
        data = r.get_json()
        assert 'network_hashrate' in data
        assert data.get('unit') == 'H/s'
        assert isinstance(data['network_hashrate'], float)

    @patch('app.bitcoinpurple_rpc_call', return_value=None)
    def test_rpc_down_returns_error(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/network-hashrate')
        assert r.status_code >= 400


# ── /api/bitcoinpurple/difficulty ────────────────────────────────────────────

class TestDifficulty:
    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_structure(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/difficulty')
        assert r.status_code == 200
        data = r.get_json()
        assert 'difficulty' in data
        assert isinstance(data['difficulty'], float)

    @patch('app.bitcoinpurple_rpc_call', return_value=None)
    def test_rpc_down_returns_error(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/difficulty')
        assert r.status_code >= 400


# ── /api/bitcoinpurple/coinbase-subsidy ──────────────────────────────────────

class TestCoinbaseSubsidy:
    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_structure(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/coinbase-subsidy')
        assert r.status_code == 200
        data = r.get_json()
        assert 'coinbase_subsidy' in data
        assert 'timestamp' in data

    @patch('app.bitcoinpurple_rpc_call', return_value=None)
    def test_rpc_down_returns_error(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/coinbase-subsidy')
        assert r.status_code >= 400


# ── /api/bitcoinpurple/peers ──────────────────────────────────────────────────

class TestPeers:
    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_structure(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/peers')
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data.get('peers'), list)
        assert data.get('total') == 1
        peer = data['peers'][0]
        assert 'addr' in peer
        assert 'inbound' in peer

    @patch('app.bitcoinpurple_rpc_call', return_value=None)
    def test_rpc_down_returns_empty_list(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/peers')
        assert r.status_code == 200
        assert r.get_json().get('peers') == []


# ── /api/bitcoinpurple/blocks/recent ─────────────────────────────────────────

class TestRecentBlocks:
    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_structure(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/blocks/recent')
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data.get('blocks'), list)
        if data['blocks']:
            blk = data['blocks'][0]
            assert 'height' in blk
            assert 'hash' in blk
            assert 'time' in blk

    @patch('app.bitcoinpurple_rpc_call', return_value=None)
    def test_rpc_down_returns_error(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/blocks/recent')
        assert r.status_code >= 400
        assert 'error' in r.get_json()

    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_partial_rpc_failure_no_crash(self, _rpc, client):
        """getblockchaininfo ok but getblockhash returns None — must not 500."""
        def _partial(method, params=None):
            if method == 'getblockchaininfo':
                return MOCK_RPC_DATA['getblockchaininfo']
            return None

        with patch('app.bitcoinpurple_rpc_call', side_effect=_partial):
            r = get(client, '/api/bitcoinpurple/blocks/recent')
        assert r.status_code == 200
        # blocks list may be empty but response must be valid JSON
        assert 'blocks' in r.get_json()


# ── /api/electrumx/stats ─────────────────────────────────────────────────────

class TestElectrumxStats:
    @patch('app.get_electrumx_stats_cached', return_value=MOCK_ELECTRUMX_STATS)
    def test_structure(self, _ex, client):
        r = get(client, '/api/electrumx/stats')
        assert r.status_code == 200
        data = r.get_json()
        assert 'stats' in data
        assert 'server_version' in data['stats']
        assert 'timestamp' in data

    @patch('app.get_electrumx_stats_cached', return_value=None)
    def test_electrumx_down_returns_error(self, _ex, client):
        r = get(client, '/api/electrumx/stats')
        assert r.status_code >= 400
        assert 'error' in r.get_json()


# ── /api/electrumx/servers ───────────────────────────────────────────────────

class TestElectrumxServers:
    @patch('app.get_electrumx_stats_cached', return_value=MOCK_ELECTRUMX_STATS)
    def test_structure(self, _ex, client):
        r = get(client, '/api/electrumx/servers')
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data.get('servers'), list)
        assert data.get('total') == len(MOCK_ELECTRUMX_STATS['active_servers'])
        assert 'timestamp' in data

    @patch('app.get_electrumx_stats_cached', return_value=None)
    def test_electrumx_down_returns_error(self, _ex, client):
        r = get(client, '/api/electrumx/servers')
        assert r.status_code >= 400


# ── /api/system/resources ────────────────────────────────────────────────────

class TestSystemResources:
    def test_structure(self, client):
        r = get(client, '/api/system/resources')
        assert r.status_code == 200
        data = r.get_json()
        assert 'cpu' in data
        assert 'memory' in data
        assert 'disk' in data
        assert 'percent' in data['cpu']
        assert 'percent' in data['memory']
        assert 'percent' in data['disk']


# ── Cache-Control headers ─────────────────────────────────────────────────────

class TestCacheHeaders:
    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_no_store(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/block-height')
        cc = r.headers.get('Cache-Control', '')
        assert 'no-store' in cc
        assert 'no-cache' in cc

    @patch('app.bitcoinpurple_rpc_call', side_effect=_rpc_dispatch)
    def test_pragma_no_cache(self, _rpc, client):
        r = get(client, '/api/bitcoinpurple/info')
        assert r.headers.get('Pragma') == 'no-cache'
