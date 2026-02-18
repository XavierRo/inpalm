#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONTAINER_NAME="nbalance-api"
TAG="${1:-latest}"

echo "============================================"
echo "  Deploy ${CONTAINER_NAME} (tag: ${TAG})"
echo "============================================"

# Charger les variables d'environnement si .env existe
if [ -f "${PROJECT_DIR}/.env" ]; then
  export $(grep -v '^#' "${PROJECT_DIR}/.env" | xargs)
fi

POSTGRES_DB="${POSTGRES_DB:-nbalance}"
POSTGRES_USER="${POSTGRES_USER:-nbalance}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-nbalance_dev}"
API_PORT="${API_PORT:-8000}"
DB_CONTAINER="nbalance-db"

# Vérifier que la BDD tourne
if ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
  echo "✗ Le conteneur ${DB_CONTAINER} n'est pas en cours d'exécution."
  echo "  Lancez d'abord : ./scripts/deploy-db.sh"
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
  --link ${DB_CONTAINER}:db \
  -e DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}" \
  -e DATABASE_URL_SYNC="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}" \
  -p ${API_PORT}:8000 \
  nbalance-api:${TAG}

echo ""
echo "✓ ${CONTAINER_NAME} démarré sur le port ${API_PORT}"

# Attendre que l'API réponde
echo "  En attente de la disponibilité..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:${API_PORT}/health > /dev/null 2>&1; then
    echo "  ✓ API prête : http://localhost:${API_PORT}/docs"
    exit 0
  fi
  sleep 1
done

echo "  ⚠ L'API n'a pas répondu dans les 30s (elle démarre peut-être encore)"
