#!/usr/bin/env bash
# Rollback controlado por SHA. Dry-run é o comportamento padrão.
set -euo pipefail

ROOT_DIR="$(dirname "$0")/.."
cd "$ROOT_DIR"

usage() {
  echo "Uso: $0 <sha-da-imagem> [--confirm]" >&2
  exit 2
}

[[ $# -ge 1 && $# -le 2 ]] || usage
ROLLBACK_TAG="$1"
CONFIRM="${2:-}"
STACK_NAME="${STACK_NAME:-cerrado}"
BACKEND_REPO="${BACKEND_REPO:-ghcr.io/fran981259/portal-cerrado-backend}"
FRONTEND_REPO="${FRONTEND_REPO:-ghcr.io/fran981259/portal-cerrado-frontend}"

if [[ ! "$ROLLBACK_TAG" =~ ^[0-9a-f]{40,64}$ ]]; then
  echo "Erro: rollback exige SHA hexadecimal completo (40-64 caracteres)." >&2
  exit 1
fi

BACKEND_IMAGE="${BACKEND_REPO}:${ROLLBACK_TAG}"
FRONTEND_IMAGE="${FRONTEND_REPO}:${ROLLBACK_TAG}"
echo "Rollback planejado: stack=$STACK_NAME sha=$ROLLBACK_TAG"
echo "Ordem: preservar logs -> atualizar backend/worker/beat/flower -> atualizar frontend -> validar health"

if [[ "$CONFIRM" != "--confirm" ]]; then
  echo "DRY-RUN: nenhuma chamada Docker foi executada. Use --confirm após aprovação explícita."
  exit 0
fi

[[ "${ROLLBACK_APPROVED:-}" == "yes" ]] || {
  echo "Erro: defina ROLLBACK_APPROVED=yes junto com --confirm." >&2
  exit 1
}
command -v docker >/dev/null || { echo "Erro: docker não encontrado." >&2; exit 1; }
[[ "$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || true)" == "active" ]] || {
  echo "Erro: Swarm não está ativo." >&2
  exit 1
}

for service in portal_cerrado celery_worker celery_beat flower; do
  docker service update --image "$BACKEND_IMAGE" "${STACK_NAME}_${service}"
done
docker service update --image "$FRONTEND_IMAGE" "${STACK_NAME}_frontend"
echo "Rollback aplicado; validar healthchecks e logs antes de retomar writers."
