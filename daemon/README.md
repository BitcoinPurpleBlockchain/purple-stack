# BitcoinPurple Core Binaries

This directory must contain the pre-compiled BitcoinPurple Core binaries used by the Docker node container.

## Download

Download from the official release repository: **https://github.com/BitcoinPurpleBlockchain/bitcoinpurplecore/releases/latest**

## Architecture

The binaries **must match the host architecture** where Docker is running.
Choose the correct archive for your platform:

| Host Architecture | Archive to download     | Common hardware                     |
|-------------------|-------------------------|-------------------------------------|
| `x86_64`          | `bitcoinpurple-linux-x86_64.tar.gz`  | Standard PCs, most VPS/cloud servers |
| `aarch64`         | `bitcoinpurple-linux-aarch64.tar.gz` | Single-board computers (Raspberry Pi 4/5, Orange Pi, etc.) |

To check your host architecture:

```bash
uname -m
```

## Required binaries

Extract the following files from the release archive and place them in this directory:

```
daemon/
  bitcoinpurpled           # Full node daemon (required)
  bitcoinpurple-cli        # RPC command-line client (required)
  bitcoinpurple-tx         # Transaction utility
  bitcoinpurple-wallet     # Wallet utility
  bitcoinpurple-util       # Low-level utility
```

## Quick setup

### Example for x86_64 (VPS/PC)

```bash
cd daemon
wget https://github.com/BitcoinPurpleBlockchain/bitcoinpurplecore/releases/latest/download/bitcoinpurple-linux-x86_64.tar.gz
tar -xzf bitcoinpurple-linux-x86_64.tar.gz
cd linux-x86_64
mv bitcoinpurple* ..
cd ..
rm -rf linux-x86_64/ && rm bitcoinpurple-linux-x86_64.tar.gz
```

### Example for aarch64 (Raspberry Pi)

```bash
cd daemon
wget https://github.com/BitcoinPurpleBlockchain/bitcoinpurplecore/releases/latest/download/bitcoinpurple-linux-aarch64.tar.gz
tar -xzf bitcoinpurple-linux-aarch64.tar.gz
cd linux-aarch64
mv bitcoinpurple* ..
cd ..
rm -rf linux-aarch64/ && rm bitcoinpurple-linux-aarch64.tar.gz
```

After placing the binaries, rebuild the node image:

```bash
docker compose build bitcoinpurpled
```
