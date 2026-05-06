# Publishing Docker Images to GHCR

This guide explains how to build and publish multi-arch images (AMD64 + ARM64) to GitHub Container Registry.

## Prerequisites

- Docker installed on both machines
- Access to the `bitcoinpurpleblockchain` GitHub organisation
- A GitHub Personal Access Token (PAT) with `write:packages` scope
  - Create one at: https://github.com/settings/tokens → "Generate new token (classic)"
  - Check: `write:packages`, `read:packages`, `delete:packages`

---

## Step 1 — ARM64 machine

Open a terminal in the project folder (`purple-stack`).

### 1a. Build the images (if not already built)

```bash
docker compose build
```

This creates locally:
- `bitcoinpurple-node:local`
- `btcp-electrumx:local`
- `bitcoinpurple-dashboard:local`

### 1b. Log in to GHCR

```bash
docker login ghcr.io
```

Enter:
- **Username:** your GitHub username
- **Password:** the PAT generated above

### 1c. Tag and push the images

```bash
docker tag bitcoinpurple-node:local ghcr.io/bitcoinpurpleblockchain/bitcoinpurple-node:latest-arm64
docker push ghcr.io/bitcoinpurpleblockchain/bitcoinpurple-node:latest-arm64

docker tag btcp-electrumx:local ghcr.io/bitcoinpurpleblockchain/btcp-electrumx:latest-arm64
docker push ghcr.io/bitcoinpurpleblockchain/btcp-electrumx:latest-arm64

docker tag bitcoinpurple-dashboard:local ghcr.io/bitcoinpurpleblockchain/bitcoinpurple-dashboard:latest-arm64
docker push ghcr.io/bitcoinpurpleblockchain/bitcoinpurple-dashboard:latest-arm64
```

---

## Step 2 — AMD64 machine

Open a terminal in the project folder (`purple-stack`).

### 2a. Build the images (if not already built)

```bash
docker compose build
```

This creates locally:
- `bitcoinpurple-node:local`
- `btcp-electrumx:local`
- `bitcoinpurple-dashboard:local`

### 2b. Log in to GHCR

```bash
docker login ghcr.io
```

Enter:
- **Username:** your GitHub username
- **Password:** the PAT generated above

### 2c. Tag and push the images

```bash
docker tag bitcoinpurple-node:local ghcr.io/bitcoinpurpleblockchain/bitcoinpurple-node:latest-amd64
docker push ghcr.io/bitcoinpurpleblockchain/bitcoinpurple-node:latest-amd64

docker tag btcp-electrumx:local ghcr.io/bitcoinpurpleblockchain/btcp-electrumx:latest-amd64
docker push ghcr.io/bitcoinpurpleblockchain/btcp-electrumx:latest-amd64

docker tag bitcoinpurple-dashboard:local ghcr.io/bitcoinpurpleblockchain/bitcoinpurple-dashboard:latest-amd64
docker push ghcr.io/bitcoinpurpleblockchain/bitcoinpurple-dashboard:latest-amd64
```

---

## Step 3 — Create the multi-arch manifest

From **either** machine, inside the project folder:

```bash
./publish.sh merge
```

This combines `latest-amd64` and `latest-arm64` into a single `latest` tag.
Docker will automatically pull the correct arch for each user's machine.

### Verify

```bash
docker buildx imagetools inspect ghcr.io/bitcoinpurpleblockchain/bitcoinpurple-node:latest
docker buildx imagetools inspect ghcr.io/bitcoinpurpleblockchain/btcp-electrumx:latest
docker buildx imagetools inspect ghcr.io/bitcoinpurpleblockchain/bitcoinpurple-dashboard:latest
```

You should see both `linux/amd64` and `linux/arm64` in the output.

---

## Step 4 — Make packages public

GHCR packages are private by default. To make them publicly pullable:

1. Go to https://github.com/orgs/bitcoinpurpleblockchain/packages
2. Click each package
3. **Package settings** → **Change visibility** → **Public**

Repeat for all 3 packages.

---

## How users pull the images

```bash
docker compose -f docker-compose.ghcr.yml up -d
```

Docker automatically pulls the correct image for their architecture (AMD64 or ARM64).

---

## Updating images in the future

Whenever you want to publish a new version:

1. **ARM64:** tag and push with `:latest-arm64` (see Step 1)
2. **AMD64:** tag and push with `:latest-amd64` (see Step 2)
3. **Merge:** `./publish.sh merge`
