"""
E2E fixtures: bring the full Docker Compose stack up before the session
and tear it down afterward.

Usage:
    pytest test/e2e/ -v --timeout=180

The stack is started with `docker compose up -d --build` and the fixture
waits up to 120 s for /api/health to return 200 before yielding.
"""

import subprocess
import time
import requests
import pytest

COMPOSE_FILE = 'docker-compose.yml'
HEALTH_URL = 'http://localhost:8080/api/health'
STARTUP_TIMEOUT = 120  # seconds


def _compose(*args):
    return subprocess.run(
        ['docker', 'compose', '-f', COMPOSE_FILE, *args],
        capture_output=True, text=True
    )


def _wait_healthy(timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(HEALTH_URL, timeout=3)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(3)
    return False


@pytest.fixture(scope='session', autouse=True)
def compose_stack():
    result = _compose('up', '-d', '--build')
    if result.returncode != 0:
        pytest.fail(f'docker compose up failed:\n{result.stderr}')

    if not _wait_healthy(STARTUP_TIMEOUT):
        _compose('logs', '--tail=50')
        _compose('down')
        pytest.fail(f'/api/health did not return 200 within {STARTUP_TIMEOUT}s')

    yield

    _compose('down')
