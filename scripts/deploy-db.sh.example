#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONTAINER_NAME="nbalance-db"

echo "============================================"
echo "  Deploy ${CONTAINER_NAME}"
echo "============================================"

# Charger les variables d'environnement si .env existe
if [ -f "${PROJECT_DIR}/.env" ]; then
  export $(grep -v '^#' "${PROJECT_DIR}/.env" | xargs)
fi

POSTGRES_DB="${POSTGRES_DB:-nbalance}"
POSTGRES_USER="${POSTGRES_USER:-nbalance}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-nbalance_dev}"
DB_PORT="${DB_PORT:-5432}"

# Vérifier si le conteneur existe déjà
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "→ Conteneur ${CONTAINER_NAME} existe déjà"
  if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "  En cours d'exécution, rien à faire."
    exit 0
  else
    echo "  Arrêté, redémarrage..."
    docker start ${CONTAINER_NAME}
    exit 0
  fi
fi

echo "→ Création du conteneur ${CONTAINER_NAME}..."

# Créer le volume s'il n'existe pas
docker volume create nbalance_pgdata 2>/dev/null || true

docker run -d \
  --name ${CONTAINER_NAME} \
  --restart unless-stopped \
  -e POSTGRES_DB=${POSTGRES_DB} \
  -e POSTGRES_USER=${POSTGRES_USER} \
  -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
  -p ${DB_PORT}:5432 \
  -v nbalance_pgdata:/var/lib/postgresql/data \
  --health-cmd="pg_isready -U ${POSTGRES_USER}" \
  --health-interval=5s \
  --health-timeout=5s \
  --health-retries=5 \
  postgres:16

echo ""
echo "✓ ${CONTAINER_NAME} démarré sur le port ${DB_PORT}"
echo "  En attente de la disponibilité..."

# Attendre que PostgreSQL soit prêt
for i in $(seq 1 30); do
  if docker exec ${CONTAINER_NAME} pg_isready -U ${POSTGRES_USER} > /dev/null 2>&1; then
    echo "  ✓ PostgreSQL prêt"
    exit 0
  fi
  sleep 1
done

echo "  ✗ Timeout — PostgreSQL n'a pas démarré dans les 30s"
exit 1
