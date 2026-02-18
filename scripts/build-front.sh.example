#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TAG="${1:-latest}"

echo "============================================"
echo "  Build nbalance-front:${TAG}"
echo "============================================"

docker build \
  -t nbalance-front:${TAG} \
  -f "${PROJECT_DIR}/frontend/Dockerfile" \
  "${PROJECT_DIR}/frontend"

echo ""
echo "✓ Image nbalance-front:${TAG} construite avec succès"
docker images nbalance-front:${TAG} --format "  Taille: {{.Size}}"
