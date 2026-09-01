#!/bin/bash
set -e
T_HOST="100.95.111.24"
T_USER="razuk"
SRC="/home/razuk/Documents/BotGram"
DST="~/BotGram"

echo "=== Deploy Portal Cerrado -> Tailscale $T_HOST ==="
echo "1. Verificando conectividade..."
ping -c1 -W2 $T_HOST || { echo "Tailscale offline"; exit 1; }

echo "2. Rsync (excluindo .venv, data/*.db, .git temporários)..."
rsync -avz --delete \
  --exclude '.venv' --exclude '__pycache__' --exclude '*.pyc' \
  --exclude 'data/atualiza_brasil.db' --exclude 'data/*.db' \
  --exclude '.next' --exclude 'node_modules' \
  --exclude '.git' \
  -e "ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no" \
  "$SRC/" "$T_USER@$T_HOST:$DST/"

echo "3. No remoto: git pull + docker compose up..."
ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no $T_USER@$T_HOST bash << 'REMOTE'
set -e
cd ~/BotGram
echo "-> git status"
git status --short
echo "-> git pull"
git pull --ff-only || echo "pull falhou, segue"
echo "-> docker compose"
if command -v docker >/dev/null 2>&1; then
  docker compose up -d --build
  sleep 5
  docker compose ps
  curl -s http://localhost:8000/health | head -c 500 || echo "health ainda não"
  curl -s http://localhost:3000 | head -c 200 || echo "frontend ainda não"
else
  echo "docker não encontrado no remoto"
fi
# re-gera sitemap com prod URL
SITE_URL=https://portalcerrado.com.br NEXT_PUBLIC_SITE_URL=https://portalcerrado.com.br python3 -c "from app.tasks.maintenance import update_sitemap; print(update_sitemap())" || true
REMOTE

echo "=== Deploy finalizado. Valide: http://100.95.111.24:3000 e http://100.95.111.24:8000/health ==="
