#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAG="${1:-latest}"

echo "============================================"
echo "  NBalance — Déploiement complet"
echo "  Tag: ${TAG}"
echo "============================================"
echo ""

# 1. Base de données
#bash "${SCRIPT_DIR}/deploy-db.sh"
#echo ""

# 2. API
bash "${SCRIPT_DIR}/deploy-api.sh" ${TAG}
echo ""

# 3. Frontend
bash "${SCRIPT_DIR}/deploy-front.sh" ${TAG}
echo ""

echo "============================================"
echo "  ✓ Déploiement terminé !"
echo ""
echo "  Frontend : http://localhost:${FRONT_PORT:-80}"
echo "  API      : http://localhost:${API_PORT:-8000}/docs"
echo "============================================"
