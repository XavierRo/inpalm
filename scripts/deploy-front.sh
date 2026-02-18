#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONTAINER_NAME="nbalance-front"
TAG="${1:-latest}"

echo "============================================"
echo "  Deploy ${CONTAINER_NAME} (tag: ${TAG})"
echo "============================================"

# Charger les variables d'environnement si .env existe
if [ -f "${PROJECT_DIR}/.env" ]; then
  export $(grep -v '^#' "${PROJECT_DIR}/.env" | xargs)
fi

FRONT_PORT="${FRONT_PORT:-80}"
API_CONTAINER="nbalance-api"

# Vérifier que l'API tourne
if ! docker ps --format '{{.Names}}' | grep -q "^${API_CONTAINER}$"; then
  echo "✗ Le conteneur ${API_CONTAINER} n'est pas en cours d'exécution."
  echo "  Lancez d'abord : ./scripts/deploy-api.sh"
  exit 1
fi

# Arrêter et supprimer l'ancien conteneur s'il existe
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "→ Arrêt de l'ancien conteneur..."
  docker stop ${CONTAINER_NAME} 2>/dev/null || true
  docker rm ${CONTAINER_NAME} 2>/dev/null || true
fi

echo "→ Lancement de ${CONTAINER_NAME}..."

docker run -d \
  --name ${CONTAINER_NAME} \
  --restart unless-stopped \
  --link ${API_CONTAINER}:nbalance-api \
  -p ${FRONT_PORT}:80 \
  nbalance-front:${TAG}

echo ""
echo "✓ ${CONTAINER_NAME} démarré sur le port ${FRONT_PORT}"
echo "  Application accessible : http://localhost:${FRONT_PORT}"
