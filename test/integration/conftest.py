"""
Auto-skip all integration tests when the Docker stack is not running.
Checks that the node RPC port (13495) is reachable on localhost.
"""

import socket
import pytest


def _port_open(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except OSError:
        return False


@pytest.fixture(scope='session', autouse=True)
def require_stack():
    # Check dashboard port (8080) — always exposed when stack is up.
    # RPC (13495) is internal-only by design.
    if not _port_open('localhost', 8080):
        pytest.skip('Docker stack not running — skipping integration tests (docker compose up -d)')
