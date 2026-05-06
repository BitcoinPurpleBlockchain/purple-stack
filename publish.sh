#!/usr/bin/env bash
set -euo pipefail

REGISTRY=ghcr.io
ORG=bitcoinpurpleblockchain
TAG=latest

declare -A DOCKERFILES=(
  [bitcoinpurple-node]=Dockerfile.node
  [btcp-electrumx]=Dockerfile.electrumx
  [bitcoinpurple-dashboard]=Dockerfile.dashboard
)
IMAGES=(bitcoinpurple-node btcp-electrumx bitcoinpurple-dashboard)

if [[ "${1:-}" == "merge" ]]; then
  echo "Creating multi-arch manifests..."
  for IMAGE in "${IMAGES[@]}"; do
    echo "  → $IMAGE"
    docker buildx imagetools create \
      --tag "$REGISTRY/$ORG/$IMAGE:$TAG" \
      "$REGISTRY/$ORG/$IMAGE:$TAG-amd64" \
      "$REGISTRY/$ORG/$IMAGE:$TAG-arm64"
  done
  echo "Done. Inspect with:"
  for IMAGE in "${IMAGES[@]}"; do
    echo "  docker buildx imagetools inspect $REGISTRY/$ORG/$IMAGE:$TAG"
  done
  exit 0
fi

ARCH=$(uname -m)
case "$ARCH" in
  x86_64)  PLATFORM=linux/amd64; PLATFORM_TAG=amd64 ;;
  aarch64) PLATFORM=linux/arm64; PLATFORM_TAG=arm64 ;;
  *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

echo "Detected: $PLATFORM ($ARCH)"
echo "Logging in to $REGISTRY..."
docker login "$REGISTRY"

for IMAGE in "${IMAGES[@]}"; do
  DOCKERFILE="${DOCKERFILES[$IMAGE]}"
  echo ""
  echo "Building $IMAGE ($PLATFORM_TAG)..."

  if [[ "$IMAGE" == "bitcoinpurple-node" ]]; then
    echo "  Downloading node binaries..."
    (cd daemon && ./download-binaries.sh)
  fi

  docker buildx build \
    --platform "$PLATFORM" \
    --push \
    -t "$REGISTRY/$ORG/$IMAGE:$TAG-$PLATFORM_TAG" \
    -f "$DOCKERFILE" .

  echo "  Pushed: $REGISTRY/$ORG/$IMAGE:$TAG-$PLATFORM_TAG"
done

echo ""
echo "All images pushed for $PLATFORM_TAG."
echo "Once both amd64 and arm64 are done, run: ./publish.sh merge"
