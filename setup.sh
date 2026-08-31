#!/usr/bin/env bash
# ============================================================
# Setup do ambiente — Atualiza Brasil
# Cria venv, instala dependências e (opcionalmente) Postgres/Redis.
# Uso: bash setup.sh
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Criando ambiente virtual (venv)..."
python3 -m venv .venv 2>/dev/null || { echo "Erro: python3-venv ausente. Instale: sudo apt install python3-venv"; exit 1; }

echo "==> Instalando dependências Python..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# --- Infra (opcional, requer sudo) ----------------------------------
if command -v systemctl >/dev/null 2>&1; then
  if ! command -v psql >/dev/null 2>&1 || ! command -v redis-server >/dev/null 2>&1; then
    echo ""
    echo "==> PostgreSQL e/ou Redis não encontrados."
    echo "    Para execução completa (recomendado), o script pode instalá-los (precisa de sudo)."
    read -r -p "    Instalar Postgres + Redis via apt? [s/N] " yn
    if [[ "${yn,,}" == "s" ]]; then
      sudo apt-get update
      sudo apt-get install -y postgresql redis-server
      sudo systemctl enable --now postgresql redis-server 2>/dev/null || true
      sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='portal_user'" | grep -q 1 || \
        sudo -u postgres psql -c "CREATE USER portal_user WITH PASSWORD 'portal_pass';"
      sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='atualiza_brasil'" | grep -q 1 || \
        sudo -u postgres psql -c "CREATE DATABASE atualiza_brasil OWNER portal_user;"
      echo "==> PostgreSQL e Redis prontos."
    else
      echo "    Sem Postgres/Redis. O sistema usará fallback SQLite (funciona, porém SQLite <> Postgres em produção)."
    fi
  else
    echo "==> PostgreSQL e Redis já instalados."
    sudo systemctl enable --now postgresql redis-server 2>/dev/null || true
  fi
fi

echo ""
echo "=================================================="
echo " Setup concluído!"
echo " Rodando na PRIMEIRA vez: bancos + API + worker + beat + frontend"
echo "  1) Abra outro terminal e rode: bash run.sh"
echo "=================================================="
