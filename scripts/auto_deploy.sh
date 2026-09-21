#!/bin/bash
# auto_deploy.sh — Deploy contínuo por "pull model" (via Git).
# Roda no servidor (cron) e, quando há mudanças no branch main, faz pull e build local.
#
# Instalar no cron (como ubuntu):
#   */5 * * * * /home/ubuntu/BotGram/scripts/auto_deploy.sh >> /home/ubuntu/BotGram/logs/auto_deploy.log 2>&1
set -euo pipefail

ROOT_DIR="$(dirname "$0")/.."
cd "$ROOT_DIR"

mkdir -p logs

# Atualiza referências remotas
git fetch origin main >/dev/null 2>&1 || {
  echo "[$(date -Is)] Falha ao buscar no Git remoto" >> logs/auto_deploy.log
  exit 1
}

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
  echo "[$(date -Is)] Nova versão detectada: ${LOCAL:0:7} -> ${REMOTE:0:7}" >> logs/auto_deploy.log
  
  if git pull origin main; then
    echo "[$(date -Is)] Pull concluído. Reconstruindo containers..." >> logs/auto_deploy.log
    if docker compose build && docker compose up -d --remove-orphans; then
      echo "[$(date -Is)] Deploy concluído com sucesso." >> logs/auto_deploy.log
    else
      echo "[$(date -Is)] ERRO: Falha ao executar docker compose." >> logs/auto_deploy.log
    fi
  else
    echo "[$(date -Is)] ERRO: Falha no git pull." >> logs/auto_deploy.log
  fi
fi