"""
E2E: full Electrum protocol handshake against the running stack.
"""

import json
import os
import socket
import pytest

HOST = 'localhost'
TCP_PORT = int(os.getenv('ELECTRUMX_TCP_PORT', '50001'))
TIMEOUT = 10.0
MAINNET_GENESIS = '000003823fbf82ea4906cbe214617ce7a70a5da29c19ecb1d65618bcf04ec015'


def _rpc(sock, method, params=None, req_id=1):
    req = json.dumps({'jsonrpc': '2.0', 'id': req_id, 'method': method, 'params': params or []}) + '\n'
    sock.sendall(req.encode())
    buf = b''
    while b'\n' not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return json.loads(buf.split(b'\n', 1)[0].decode())


@pytest.mark.e2e
def test_server_version_handshake():
    s = socket.create_connection((HOST, TCP_PORT), timeout=TIMEOUT)
    resp = _rpc(s, 'server.version', ['e2e-test', '1.4'])
    s.close()
    assert 'result' in resp
    assert isinstance(resp['result'], list)
    assert len(resp['result']) == 2  # [server_version, protocol_version]


@pytest.mark.e2e
def test_server_features_genesis():
    s = socket.create_connection((HOST, TCP_PORT), timeout=TIMEOUT)
    resp = _rpc(s, 'server.features')
    s.close()
    assert resp['result']['genesis_hash'] == MAINNET_GENESIS


@pytest.mark.e2e
def test_headers_subscribe():
    s = socket.create_connection((HOST, TCP_PORT), timeout=TIMEOUT)
    # server.version first (required by protocol before other calls)
    _rpc(s, 'server.version', ['e2e-test', '1.4'], req_id=0)
    resp = _rpc(s, 'blockchain.headers.subscribe', req_id=2)
    s.close()
    assert 'result' in resp
    result = resp['result']
    # Result is either the header dict or a [header, height] list depending on protocol
    if isinstance(result, dict):
        assert 'height' in result or 'block_height' in result
    elif isinstance(result, list):
        assert len(result) >= 1


@pytest.mark.e2e
def test_clean_disconnect():
    """Closing the socket without sending anything should not hang."""
    s = socket.create_connection((HOST, TCP_PORT), timeout=TIMEOUT)
    s.close()  # clean close — server should not crash
