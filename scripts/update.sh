#!/bin/bash
# Atualiza Portal Cerrado em 1 comando — para rodar no host Razuk (100.95.111.24)
# Uso: ./scripts/update.sh  (ou: bash scripts/update.sh)
set -e
cd "$(dirname "$0")/.."
echo "== Portal Cerrado — Update 1-clique =="
echo "[1/4] git pull"
git pull --ff-only
echo "[2/4] docker build backend"
docker build -t botgram-atualiza_brasil:latest .
echo "[3/4] docker build frontend"
docker build -t botgram-frontend:latest ./frontend
echo "[4/4] redeploy stack botgram"
# tenta via docker stack (Swarm) ou compose
if docker stack ls 2>/dev/null | grep -q botgram; then
  docker stack deploy -c docker-compose.yml botgram --with-registry-auth
else
  docker compose up -d --build
fi
echo "== Pronto! =="
echo "Frontend: http://100.95.111.24:3000"
echo "API:      http://100.95.111.24:8000/health"
echo "Flower:   http://100.95.111.24:5555"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "botgram|postgres|redis" || true
