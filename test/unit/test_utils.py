"""
Tests for pure utility functions in web-dashboard/app.py:
- parse_services_ports()
- parse_addnode_hosts()
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web-dashboard'))
from app import parse_services_ports, parse_addnode_hosts


# ── parse_services_ports ──────────────────────────────────────────────────────

class TestParseServicesPorts:
    def test_full_services_string(self):
        s = 'tcp://0.0.0.0:51001,ssl://0.0.0.0:51002,rpc://0.0.0.0:8000'
        assert parse_services_ports(s) == (51001, 51002)

    def test_tcp_only(self):
        assert parse_services_ports('tcp://0.0.0.0:51001') == (51001, None)

    def test_ssl_only(self):
        assert parse_services_ports('ssl://0.0.0.0:51002') == (None, 51002)

    def test_empty_string(self):
        assert parse_services_ports('') == (None, None)

    def test_non_numeric_port_returns_none(self):
        tcp, ssl = parse_services_ports('tcp://0.0.0.0:abc,ssl://0.0.0.0:xyz')
        assert tcp is None
        assert ssl is None

    def test_whitespace_around_items(self):
        s = ' tcp://0.0.0.0:51001 , ssl://0.0.0.0:51002 '
        tcp, ssl = parse_services_ports(s)
        assert tcp == 51001
        assert ssl == 51002

    def test_default_ports_50001_50002(self):
        s = 'tcp://0.0.0.0:50001,ssl://0.0.0.0:50002'
        assert parse_services_ports(s) == (50001, 50002)

    def test_no_port_segment_returns_none(self):
        # URL without a colon after host
        tcp, ssl = parse_services_ports('tcp://localhost,ssl://localhost')
        assert tcp is None
        assert ssl is None


# ── parse_addnode_hosts ───────────────────────────────────────────────────────

class TestParseAddnodeHosts:
    def _write_conf(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_single_host_with_port(self):
        path = self._write_conf('addnode=1.2.3.4:13496\n')
        assert parse_addnode_hosts(path) == ['1.2.3.4']

    def test_host_without_port(self):
        path = self._write_conf('addnode=mynode.example.com\n')
        assert parse_addnode_hosts(path) == ['mynode.example.com']

    def test_multiple_hosts(self):
        path = self._write_conf(
            'addnode=1.2.3.4:13496\naddnode=5.6.7.8:13496\n'
        )
        result = parse_addnode_hosts(path)
        assert '1.2.3.4' in result
        assert '5.6.7.8' in result
        assert len(result) == 2

    def test_duplicates_deduplicated(self):
        path = self._write_conf(
            'addnode=1.2.3.4:13496\naddnode=1.2.3.4:13496\n'
        )
        assert parse_addnode_hosts(path) == ['1.2.3.4']

    def test_comments_ignored(self):
        path = self._write_conf(
            '# this is a comment\naddnode=1.2.3.4\n# another comment\n'
        )
        assert parse_addnode_hosts(path) == ['1.2.3.4']

    def test_empty_values_skipped(self):
        path = self._write_conf('addnode=\naddnode=1.2.3.4\n')
        assert parse_addnode_hosts(path) == ['1.2.3.4']

    def test_other_keys_ignored(self):
        path = self._write_conf(
            'rpcuser=foo\nrpcpassword=bar\naddnode=1.2.3.4\n'
        )
        assert parse_addnode_hosts(path) == ['1.2.3.4']

    def test_file_not_found_returns_empty(self):
        result = parse_addnode_hosts('/nonexistent/path/no.conf')
        assert result == []

    def test_empty_file_returns_empty(self):
        path = self._write_conf('')
        assert parse_addnode_hosts(path) == []
