#!/usr/bin/env bash
# ============================================================
# Executa o Atualiza Brasil (dev)
# Inicia: API (com agendador local), e opcionalmente Frontend.
# Celery/Redis são opcionais — sem eles, o agendador embutido
# mantém as notícias atualizadas a cada 30 min.
# Uso: bash run.sh
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

API_PORT="${API_PORT:-8001}"
ENABLE_LOCAL_SCHEDULER="${ENABLE_LOCAL_SCHEDULER:-1}"

if [ ! -x .venv/bin/uvicorn ]; then
  echo "Ambiente não configurado. Rodando setup.sh..."
  bash setup.sh
fi

export ENABLE_LOCAL_SCHEDULER

echo "==> Iniciando API (porta ${API_PORT}) com agendador local..."
ENABLE_LOCAL_SCHEDULER=1 .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "${API_PORT}" \
  --lifespan on &
API_PID=$!

# Pequena espera para dar tempo da primeira execução do pipeline
echo "==> Aguardando pipeline inicial (primeira leva de notícias)..."
sleep 20
echo "    Conferindo:"
curl -s "http://127.0.0.1:${API_PORT}/health" && echo

if [ "${START_FRONTEND:-1}" == "1" ] && [ -d frontend/node_modules ]; then
  echo "==> Iniciando Frontend (Next.js, porta 3000)..."
  (cd frontend && npm run dev >/tmp/frontend_dev.log 2>&1) &
  FRONT_PID=$!
else
  FRONT_PID=""
  echo "==> Frontend não iniciado (START_FRONTEND=0 ou node_modules ausente)."
fi

echo ""
echo "=============================================="
echo "  API      : http://localhost:${API_PORT}"
echo "  Notícias : http://localhost:${API_PORT}/api/news"
if [ -n "$FRONT_PID" ]; then echo "  Front    : http://localhost:3000"; fi
echo "  PIDs     : API=${API_PID} Front=${FRONT_PID:---}"
echo "  Dica     : tail -f /tmp/uvicorn*.log para logs"
echo "=============================================="
echo "Pressione Ctrl+C para encerrar."
wait
