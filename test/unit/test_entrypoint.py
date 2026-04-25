"""
Tests for entrypoint.sh logic.

We create a patched copy of entrypoint.sh with the hardcoded BITCOINPURPLE_CONF
path replaced by a temp file path, then source it in a subprocess while
stubbing out external calls (curl, openssl, python3, exec).
"""

import os
import re
import subprocess
import tempfile
import textwrap
import pytest

ENTRYPOINT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'entrypoint.sh')
)


def _make_patched_entrypoint(conf_path: str) -> str:
    """Return path to a temp copy of entrypoint.sh with BITCOINPURPLE_CONF replaced
    and the final `exec` call neutered so the shell stays alive for our assertions."""
    with open(ENTRYPOINT) as f:
        src = f.read()
    # Replace the hardcoded conf path assignment at the top
    patched = re.sub(
        r'BITCOINPURPLE_CONF="[^"]+"',
        f'BITCOINPURPLE_CONF="{conf_path}"',
        src,
        count=1,
    )
    # Remove `set -e` so failures in non-critical parts (chmod /certs) don't kill the shell.
    patched = re.sub(r'^\s*set -e\s*$', '# set -e removed for tests', patched, flags=re.MULTILINE)
    # Replace `exec /usr/local/bin/electrumx_server` with a no-op.
    # We can't override bash's exec builtin with a function, so we patch the source.
    patched = re.sub(r'\bexec /usr/local/bin/electrumx_server\b', ': # exec stubbed', patched)
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False)
    tmp.write(patched)
    tmp.close()
    return tmp.name


def _run(conf_content: str, extra_env: dict = None) -> subprocess.CompletedProcess:
    """
    Write conf_content to a temp file, patch entrypoint.sh to point at it,
    source it in a bash subprocess (stubbing external calls), and return
    the subprocess result with RPC_USER/PASSWORD/PORT/DAEMON_URL echoed.
    """
    # Write conf
    conf_f = tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False)
    conf_f.write(conf_content)
    conf_f.close()

    script_path = _make_patched_entrypoint(conf_f.name)

    snippet = textwrap.dedent(f"""\
        #!/bin/bash
        # Stub external calls so sourcing doesn't hang or fail on missing tools
        curl() {{ true; }}
        openssl() {{ true; }}
        python3() {{ true; }}
        # Prevent exec from actually launching electrumx_server
        exec() {{ true; }}

        # Disable errexit so we can capture output even on validation failures
        set +e

        source "{script_path}"

        echo "RPC_USER=$RPC_USER"
        echo "RPC_PASSWORD=$RPC_PASSWORD"
        echo "RPC_PORT=$RPC_PORT"
        echo "DAEMON_URL=$DAEMON_URL"
    """)

    env = os.environ.copy()
    env['NET'] = 'mainnet'
    if extra_env:
        env.update(extra_env)

    result = subprocess.run(['bash', '-c', snippet], capture_output=True, text=True, env=env)

    os.unlink(conf_f.name)
    os.unlink(script_path)
    return result


def _parse_vars(output: str) -> dict:
    result = {}
    for line in output.splitlines():
        if '=' in line:
            key, _, value = line.partition('=')
            result[key.strip()] = value.strip()
    return result


# ── Credential extraction ─────────────────────────────────────────────────────

class TestCredentialExtraction:
    def test_extracts_rpcuser(self):
        r = _run('rpcuser=alice\nrpcpassword=hunter2\n')
        assert _parse_vars(r.stdout).get('RPC_USER') == 'alice'

    def test_extracts_rpcpassword(self):
        r = _run('rpcuser=alice\nrpcpassword=hunter2\n')
        assert _parse_vars(r.stdout).get('RPC_PASSWORD') == 'hunter2'

    def test_credentials_with_spaces_stripped(self):
        r = _run('rpcuser= bob \nrpcpassword= s3cr3t \n')
        vars_ = _parse_vars(r.stdout)
        assert vars_.get('RPC_USER') == 'bob'
        assert vars_.get('RPC_PASSWORD') == 's3cr3t'

    def test_missing_conf_exits_nonzero(self):
        """When conf is missing the script must exit with non-zero and print ERROR."""
        # Build a patched script pointing at a nonexistent path
        script_path = _make_patched_entrypoint('/tmp/does_not_exist_xyz_btcp.conf')
        snippet = textwrap.dedent(f"""\
            #!/bin/bash
            curl() {{ true; }}; openssl() {{ true; }}; python3() {{ true; }}; exec() {{ true; }}
            source "{script_path}"
        """)
        r = subprocess.run(['bash', '-c', snippet], capture_output=True, text=True)
        os.unlink(script_path)
        assert r.returncode != 0
        assert 'ERROR' in (r.stdout + r.stderr)

    def test_missing_credentials_exits_nonzero(self):
        r = _run('# no credentials here\n')
        assert r.returncode != 0


# ── RPC port fallback ─────────────────────────────────────────────────────────

class TestRpcPortFallback:
    def test_mainnet_default_port(self):
        r = _run('rpcuser=u\nrpcpassword=p\n', extra_env={'NET': 'mainnet'})
        assert _parse_vars(r.stdout).get('RPC_PORT') == '13495'

    def test_testnet_default_port(self):
        r = _run('rpcuser=u\nrpcpassword=p\n', extra_env={'NET': 'testnet'})
        assert _parse_vars(r.stdout).get('RPC_PORT') == '23495'

    def test_explicit_port_in_conf_overrides_default(self):
        r = _run('rpcuser=u\nrpcpassword=p\nrpcport=9999\n', extra_env={'NET': 'mainnet'})
        assert _parse_vars(r.stdout).get('RPC_PORT') == '9999'


# ── DAEMON_URL construction ───────────────────────────────────────────────────

class TestDaemonUrl:
    def test_daemon_url_format(self):
        r = _run('rpcuser=foo\nrpcpassword=bar\n', extra_env={'NET': 'mainnet'})
        url = _parse_vars(r.stdout).get('DAEMON_URL', '')
        assert url == 'http://foo:bar@bitcoinpurpled:13495/'

    def test_daemon_url_uses_extracted_port(self):
        r = _run('rpcuser=foo\nrpcpassword=bar\nrpcport=8888\n')
        url = _parse_vars(r.stdout).get('DAEMON_URL', '')
        assert ':8888/' in url
