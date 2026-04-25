"""
Tests for authentication and IP-trust logic in web-dashboard/app.py.

Covers:
- is_trusted_client_ip() for all address families and edge cases
- API key validation (X-API-Key, Bearer, wrong key, empty env)
- Dashboard Basic Auth flow
- X-Forwarded-For spoofing (must NOT bypass auth)
"""

import os
import pytest
from unittest.mock import patch

sys_path_added = False


def _setup_env(monkeypatch, api_key='test-key-abc'):
    monkeypatch.setenv('API_KEY', api_key)
    monkeypatch.setenv('DASHBOARD_AUTH_USERNAME', 'admin')
    monkeypatch.setenv('DASHBOARD_AUTH_PASSWORD', 'secret')


# ── is_trusted_client_ip ─────────────────────────────────────────────────────

class TestIsTrustedClientIp:
    @pytest.fixture(autouse=True)
    def _import(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web-dashboard'))
        from app import is_trusted_client_ip
        self.fn = is_trusted_client_ip

    def test_loopback_ipv4(self):
        assert self.fn('127.0.0.1') is True

    def test_loopback_ipv4_other(self):
        assert self.fn('127.0.0.2') is True

    def test_loopback_ipv6(self):
        assert self.fn('::1') is True

    def test_rfc1918_10(self):
        assert self.fn('10.0.0.1') is True

    def test_rfc1918_172(self):
        assert self.fn('172.16.0.1') is True

    def test_rfc1918_172_upper(self):
        assert self.fn('172.31.255.255') is True

    def test_rfc1918_192(self):
        assert self.fn('192.168.1.100') is True

    def test_external_google_dns(self):
        assert self.fn('8.8.8.8') is False

    def test_external_cloudflare(self):
        assert self.fn('1.1.1.1') is False

    def test_external_172_outside_range(self):
        # 172.32.x.x is outside 172.16/12
        assert self.fn('172.32.0.1') is False

    def test_empty_string(self):
        assert self.fn('') is False

    def test_none(self):
        assert self.fn(None) is False

    def test_invalid_string(self):
        assert self.fn('not-an-ip') is False

    def test_ipv6_mapped_loopback(self):
        # ::ffff:127.0.0.1 is IPv4-mapped loopback
        assert self.fn('::ffff:127.0.0.1') is True

    def test_ipv6_mapped_rfc1918(self):
        assert self.fn('::ffff:10.0.0.1') is True

    def test_ipv6_mapped_external(self):
        assert self.fn('::ffff:8.8.8.8') is False


# ── API key auth (external clients hitting /api/*) ────────────────────────────

class TestApiKeyAuth:
    @pytest.fixture(autouse=True)
    def _patch_rpc(self):
        with patch('app.bitcoinpurple_rpc_call', return_value=None), \
             patch('app.get_electrumx_stats_cached', return_value=None):
            yield

    def test_external_no_key_returns_401(self, client, monkeypatch):
        _setup_env(monkeypatch)
        r = client.get('/api/health', environ_base={'REMOTE_ADDR': '8.8.8.8'})
        assert r.status_code == 401
        assert 'error' in r.get_json()

    def test_external_valid_xapikey_passes(self, client, monkeypatch):
        _setup_env(monkeypatch, api_key='my-secret-key')
        r = client.get('/api/health',
                       environ_base={'REMOTE_ADDR': '8.8.8.8'},
                       headers={'X-API-Key': 'my-secret-key'})
        assert r.status_code != 401

    def test_external_valid_bearer_passes(self, client, monkeypatch):
        _setup_env(monkeypatch, api_key='my-secret-key')
        r = client.get('/api/health',
                       environ_base={'REMOTE_ADDR': '8.8.8.8'},
                       headers={'Authorization': 'Bearer my-secret-key'})
        assert r.status_code != 401

    def test_external_wrong_key_returns_401(self, client, monkeypatch):
        _setup_env(monkeypatch, api_key='correct-key')
        r = client.get('/api/health',
                       environ_base={'REMOTE_ADDR': '8.8.8.8'},
                       headers={'X-API-Key': 'wrong-key'})
        assert r.status_code == 401

    def test_trusted_ip_no_key_passes(self, client, monkeypatch):
        _setup_env(monkeypatch)
        r = client.get('/api/health', environ_base={'REMOTE_ADDR': '127.0.0.1'})
        assert r.status_code != 401

    def test_api_key_not_configured_returns_503(self, client, monkeypatch):
        monkeypatch.setenv('API_KEY', '')
        r = client.get('/api/health', environ_base={'REMOTE_ADDR': '8.8.8.8'})
        assert r.status_code == 503

    def test_xforwardedfor_spoofing_blocked(self, client, monkeypatch):
        """An external IP passing X-Forwarded-For: 127.0.0.1 must still get 401."""
        _setup_env(monkeypatch)
        r = client.get('/api/health',
                       environ_base={'REMOTE_ADDR': '8.8.8.8'},
                       headers={'X-Forwarded-For': '127.0.0.1'})
        assert r.status_code == 401

    def test_all_api_routes_enforce_auth(self, client, monkeypatch):
        _setup_env(monkeypatch)
        routes = [
            '/api/health',
            '/api/bitcoinpurple/info',
            '/api/bitcoinpurple/block-height',
            '/api/bitcoinpurple/network-hashrate',
            '/api/bitcoinpurple/difficulty',
            '/api/bitcoinpurple/coinbase-subsidy',
            '/api/bitcoinpurple/peers',
            '/api/bitcoinpurple/blocks/recent',
            '/api/electrumx/stats',
            '/api/electrumx/servers',
            '/api/system/resources',
        ]
        for route in routes:
            r = client.get(route, environ_base={'REMOTE_ADDR': '8.8.8.8'})
            assert r.status_code == 401, (
                f"{route} returned {r.status_code}, expected 401 for unauthenticated external client"
            )


# ── Dashboard Basic Auth (HTML pages, non-/api/ paths) ───────────────────────

class TestDashboardBasicAuth:
    def test_external_without_auth_returns_401(self, client, monkeypatch):
        _setup_env(monkeypatch)
        r = client.get('/', environ_base={'REMOTE_ADDR': '8.8.8.8'})
        assert r.status_code == 401
        assert 'WWW-Authenticate' in r.headers

    def test_external_with_correct_basic_auth_passes(self, client, monkeypatch):
        import base64
        _setup_env(monkeypatch)
        creds = base64.b64encode(b'admin:secret').decode()
        r = client.get('/',
                       environ_base={'REMOTE_ADDR': '8.8.8.8'},
                       headers={'Authorization': f'Basic {creds}'})
        assert r.status_code != 401

    def test_external_with_wrong_basic_auth_returns_401(self, client, monkeypatch):
        import base64
        _setup_env(monkeypatch)
        creds = base64.b64encode(b'admin:wrongpass').decode()
        r = client.get('/',
                       environ_base={'REMOTE_ADDR': '8.8.8.8'},
                       headers={'Authorization': f'Basic {creds}'})
        assert r.status_code == 401

    def test_trusted_ip_no_auth_needed(self, client, monkeypatch):
        _setup_env(monkeypatch)
        r = client.get('/', environ_base={'REMOTE_ADDR': '127.0.0.1'})
        assert r.status_code != 401

    def test_dashboard_auth_not_configured_returns_503(self, client, monkeypatch):
        import base64
        monkeypatch.setenv('DASHBOARD_AUTH_USERNAME', '')
        monkeypatch.setenv('DASHBOARD_AUTH_PASSWORD', '')
        r = client.get('/', environ_base={'REMOTE_ADDR': '8.8.8.8'})
        assert r.status_code == 503
