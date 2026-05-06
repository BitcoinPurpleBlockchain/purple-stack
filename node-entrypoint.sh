#!/bin/bash
set -e

if [ -z "${RPC_USER:-}" ] || [ -z "${RPC_PASSWORD:-}" ]; then
    echo "ERROR: RPC_USER and RPC_PASSWORD must be set in .env"
    echo "Copy .env.example to .env and fill in the credentials."
    exit 1
fi

CONF="/root/.bitcoinpurple/bitcoinpurple.conf"
EXAMPLE="/root/.bitcoinpurple/bitcoinpurple.conf.example"

# First run: generate conf from example
if [ ! -f "$CONF" ]; then
    if [ ! -f "$EXAMPLE" ]; then
        echo "ERROR: $EXAMPLE not found — cannot generate bitcoinpurple.conf"
        exit 1
    fi
    cp "$EXAMPLE" "$CONF"
    echo ">> Generated bitcoinpurple.conf from bitcoinpurple.conf.example"
fi

# Inject credentials (remove stale lines, prepend fresh ones)
sed -i '/^rpcuser=/d; /^rpcpassword=/d' "$CONF"
TMP=$(mktemp)
printf 'rpcuser=%s\nrpcpassword=%s\n' "${RPC_USER}" "${RPC_PASSWORD}" | cat - "$CONF" > "$TMP"
mv "$TMP" "$CONF"

exec bitcoinpurpled \
  -conf="$CONF" \
  -datadir=/root/.bitcoinpurple \
  -daemon=0 \
  -printtoconsole=1
