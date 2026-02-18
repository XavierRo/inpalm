#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TAG="${1:-latest}"

echo "============================================"
echo "  Build nbalance-api:${TAG}"
echo "============================================"

docker build \
  -t nbalance-api:${TAG} \
  -f "${PROJECT_DIR}/backend/Dockerfile" \
  "${PROJECT_DIR}/backend"

echo ""
echo "✓ Image nbalance-api:${TAG} construite avec succès"
docker images nbalance-api:${TAG} --format "  Taille: {{.Size}}"
