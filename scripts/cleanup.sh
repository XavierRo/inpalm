#!/bin/bash
set -e

echo "============================================"
echo "  NBalance — Nettoyage"
echo "============================================"

for CONTAINER in nbalance-front nbalance-api nbalance-db; do
  if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "→ Arrêt et suppression de ${CONTAINER}..."
    docker stop ${CONTAINER} 2>/dev/null || true
    docker rm ${CONTAINER} 2>/dev/null || true
    echo "  ✓ ${CONTAINER} supprimé"
  else
    echo "  ${CONTAINER} n'existe pas, skip"
  fi
done

echo ""
read -p "Supprimer aussi le volume PostgreSQL (données) ? [y/N] " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
  docker volume rm nbalance_pgdata 2>/dev/null || true
  echo "  ✓ Volume supprimé"
fi

echo ""
echo "✓ Nettoyage terminé"
