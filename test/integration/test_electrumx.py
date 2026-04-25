"""
Integration tests: ElectrumX server protocol.
Requires stack to be up (docker compose up -d).
"""

import json
import socket
import ssl
import pytest

MAINNET_GENESIS = '000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015'
HOST = 'localhost'
TCP_PORT = 51001
SSL_PORT = 51002
TIMEOUT = 5.0


def _send_recv(sock, method, params=None, req_id=1):
    req = json.dumps({'jsonrpc': '2.0', 'id': req_id, 'method': method, 'params': params or []}) + '\n'
    sock.sendall(req.encode())
    buf = b''
    while b'\n' not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    line = buf.split(b'\n', 1)[0].decode()
    return json.loads(line)


def _ssl_sock():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    raw = socket.create_connection((HOST, SSL_PORT), timeout=TIMEOUT)
    return ctx.wrap_socket(raw, server_hostname=HOST)


# ── TCP ───────────────────────────────────────────────────────────────────────

@pytest.mark.integration
def test_tcp_port_open():
    try:
        s = socket.create_connection((HOST, TCP_PORT), timeout=TIMEOUT)
        s.close()
    except OSError as e:
        pytest.fail(f'ElectrumX TCP port {TCP_PORT} not reachable: {e}')


@pytest.mark.integration
def test_tcp_server_version_strings():
    """server.version must return [server_string, protocol_version] — both non-empty."""
    s = socket.create_connection((HOST, TCP_PORT), timeout=TIMEOUT)
    resp = _send_recv(s, 'server.version', ['test-client', '1.4'])
    s.close()
    assert 'result' in resp, f'No result in server.version response: {resp}'
    result = resp['result']
    assert isinstance(result, list) and len(result) == 2, (
        f'Expected [server_ver, protocol_ver], got: {result}'
    )
    server_ver, protocol_ver = result
    assert server_ver, f'Server version string is empty: {result}'
    assert protocol_ver, f'Protocol version string is empty: {result}'


@pytest.mark.integration
def test_tcp_server_features_genesis():
    """Genesis hash must match mainnet exactly — wrong chain = wrong coin."""
    s = socket.create_connection((HOST, TCP_PORT), timeout=TIMEOUT)
    resp = _send_recv(s, 'server.features')
    s.close()
    assert 'result' in resp
    genesis = resp['result'].get('genesis_hash', '')
    assert genesis == MAINNET_GENESIS, f'Expected {MAINNET_GENESIS}, got {genesis!r}'


@pytest.mark.integration
def test_tcp_server_features_version():
    s = socket.create_connection((HOST, TCP_PORT), timeout=TIMEOUT)
    resp = _send_recv(s, 'server.features')
    s.close()
    version = resp['result'].get('server_version', '')
    assert 'ElectrumX' in version, f'Unexpected server_version: {version!r}'


@pytest.mark.integration
def test_tcp_electrumx_has_indexed_blocks():
    """ElectrumX must be able to return a real block header — proves indexing is live."""
    s = socket.create_connection((HOST, TCP_PORT), timeout=TIMEOUT)
    _send_recv(s, 'server.version', ['test-client', '1.4'], req_id=0)
    resp = _send_recv(s, 'blockchain.block.header', [1], req_id=1)
    s.close()
    assert 'result' in resp, f'blockchain.block.header failed: {resp}'
    header_hex = resp['result']
    assert isinstance(header_hex, str) and len(header_hex) == 160, (
        f'Block header at height 1 has unexpected format: {header_hex!r}'
    )


# ── SSL ───────────────────────────────────────────────────────────────────────

@pytest.mark.integration
def test_ssl_port_open():
    try:
        s = socket.create_connection((HOST, SSL_PORT), timeout=TIMEOUT)
        s.close()
    except OSError as e:
        pytest.fail(f'ElectrumX SSL port {SSL_PORT} not reachable: {e}')


@pytest.mark.integration
def test_ssl_server_version_strings():
    """SSL server.version must return valid [server_string, protocol_version]."""
    wrapped = _ssl_sock()
    resp = _send_recv(wrapped, 'server.version', ['test-client', '1.4'])
    wrapped.close()
    assert 'result' in resp, f'No result in SSL server.version: {resp}'
    result = resp['result']
    assert isinstance(result, list) and len(result) == 2
    assert result[0] and result[1], f'Empty version strings: {result}'


@pytest.mark.integration
def test_ssl_server_features_genesis():
    """Genesis hash over SSL must match mainnet."""
    wrapped = _ssl_sock()
    resp = _send_recv(wrapped, 'server.features')
    wrapped.close()
    assert resp['result'].get('genesis_hash') == MAINNET_GENESIS
