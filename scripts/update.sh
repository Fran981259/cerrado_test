#!/bin/bash
# Atualiza Portal Cerrado em 1 comando — host Razuk (100.95.111.24)
set -e
cd "$(dirname "$0")/.."

echo "== Portal Cerrado — Update 1-clique =="
echo "[1/5] git pull"
git pull --ff-only

echo "[2/5] docker build backend"
docker build -t botgram-atualiza_brasil:latest .

echo "[3/5] docker build frontend"
docker build -t botgram-frontend:latest ./frontend

echo "[4/5] redeploy stack (aplica qualquer mudança no docker-compose.yml)"
docker stack deploy -c docker-compose.yml botgram --with-registry-auth

echo "[5/5] forçar recriação dos containers com a imagem nova (o pulo do gato)"
docker service update --force --image botgram-atualiza_brasil:latest botgram_atualiza_brasil
docker service update --force --image botgram-atualiza_brasil:latest botgram_celery_worker
docker service update --force --image botgram-atualiza_brasil:latest botgram_celery_beat
docker service update --force --image botgram-frontend:latest botgram_frontend

echo "== Pronto! =="
echo "Frontend: http://100.95.111.24:3000"
echo "API:      http://100.95.111.24:8000/health"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "botgram|postgres|redis" || true