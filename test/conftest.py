"""Shared fixtures for all test layers."""

import os
import sys
import pytest

# Make web-dashboard importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web-dashboard'))

# Minimal env so app module-level code doesn't crash on import
os.environ.setdefault('API_KEY', 'test-api-key-for-pytest')
os.environ.setdefault('DASHBOARD_AUTH_USERNAME', 'admin')
os.environ.setdefault('DASHBOARD_AUTH_PASSWORD', 'testpass')


@pytest.fixture(scope='session')
def flask_app():
    from app import app
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(flask_app):
    with flask_app.test_client() as c:
        yield c
