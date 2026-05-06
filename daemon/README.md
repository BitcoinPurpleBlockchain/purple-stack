# BitcoinPurple Core Binaries

This directory contains the pre-compiled BitcoinPurple Core binaries used by the Docker node container.

## Automatic download (default)

No manual action is required. When running `docker compose up -d --build`, the build process automatically downloads the latest available release from GitHub and places the binaries inside the image.

If binaries are already present in this directory, the download is skipped and the existing files are used instead.

## Pinning a specific version

If you need to run a specific version of the node, place the desired binaries directly in this directory before building:

```
daemon/
  bitcoinpurpled           # Full node daemon (required)
  bitcoinpurple-cli        # RPC command-line client (required)
```

Then rebuild the node image:

```bash
docker compose build bitcoinpurpled
```

The build process will detect the binaries and skip the automatic download, using your provided files instead.

## Manual download (optional)

The helper script can also be used outside of Docker to download binaries manually:

```bash
cd daemon
./download-binaries.sh
```

### Script options

```bash
./download-binaries.sh --help
```

Common examples:

```bash
# default: Linux + auto-detected arch
./download-binaries.sh

# force a specific platform and architecture
./download-binaries.sh --platform linux --arch x86_64
./download-binaries.sh --platform linux --arch aarch64

# download Windows binaries (.exe)
./download-binaries.sh --platform windows --arch x86_64
```

## Architecture notes

For this stack, Docker needs Linux binaries matching your host CPU architecture.

- `x86_64` / `amd64` — most servers and desktops
- `aarch64` / `arm64` — Raspberry Pi 4/5 (64-bit OS), ARM servers
- `armv7l` — 32-bit ARM builds (not the default setup for this stack)

Check your architecture:

```bash
uname -m
```
