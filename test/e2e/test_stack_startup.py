"""
E2E: verify all three containers start cleanly and the stack is healthy.
"""

import subprocess
import requests
import pytest

BASE = 'http://localhost:8080'
EXPECTED_CONTAINERS = [
    'bitcoinpurple-node',
    'electrumx-server',
    'bitcoinpurple-dashboard',
]


def _running_containers():
    r = subprocess.run(
        ['docker', 'ps', '--format', '{{.Names}}'],
        capture_output=True, text=True
    )
    return r.stdout.splitlines()


@pytest.mark.e2e
def test_all_containers_running():
    running = _running_containers()
    for name in EXPECTED_CONTAINERS:
        assert name in running, f'Container {name!r} is not running'


@pytest.mark.e2e
def test_health_returns_200():
    r = requests.get(f'{BASE}/api/health', timeout=10)
    assert r.status_code == 200


@pytest.mark.e2e
def test_health_not_all_down():
    data = requests.get(f'{BASE}/api/health', timeout=10).json()
    services = data.get('services', {})
    all_down = all(v == 'down' for v in services.values())
    assert not all_down, f'All services reported down: {services}'


@pytest.mark.e2e
def test_no_fatal_in_node_logs():
    r = subprocess.run(
        ['docker', 'logs', '--tail', '100', 'bitcoinpurple-node'],
        capture_output=True, text=True
    )
    combined = r.stdout + r.stderr
    assert 'FATAL' not in combined, 'FATAL found in node logs'


@pytest.mark.e2e
def test_no_fatal_in_electrumx_logs():
    r = subprocess.run(
        ['docker', 'logs', '--tail', '100', 'electrumx-server'],
        capture_output=True, text=True
    )
    combined = r.stdout + r.stderr
    assert 'FATAL' not in combined, 'FATAL found in electrumx logs'
