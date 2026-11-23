#!/usr/bin/env bash
#
# docker-build.sh — build the Docker image for the container sandbox variant.
#
# Builds pi-team-sandbox:latest from the Dockerfile that lives next to this
# script. The image contains only OS packages (git, python3, ca-certificates)
# on debian:12-slim — node and the pi install are mounted read-only at
# runtime by run-docker-test.sh, and no secrets are baked into the image.
#
# Idempotent: rebuilds the image on every run. Prints the image id at the end.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="pi-team-sandbox:latest"

docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"

IMAGE_ID="$(docker image inspect --format '{{.Id}}' "$IMAGE_NAME")"
echo "Built $IMAGE_NAME"
echo "Image id: $IMAGE_ID"
