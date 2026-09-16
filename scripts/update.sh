#!/bin/bash
# Atualiza Portal Cerrado em 1 comando
set -euo pipefail

ROOT_DIR="$(dirname "$0")/.."
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

required_vars=(POSTGRES_USER POSTGRES_PASSWORD REDIS_PASSWORD PUBLISH_API_KEY NEXT_PUBLIC_SITE_URL FLOWER_USER FLOWER_PASSWORD)
for var in "${required_vars[@]}"; do
  if [ -z "${!var:-}" ]; then
    echo "Erro: $var nao configurado" >&2
    exit 1
  fi
done

STACK_NAME="${STACK_NAME:-cerrado}"
BACKEND_REPO="${BACKEND_REPO:-ghcr.io/fran981259/portal-cerrado-backend}"
FRONTEND_REPO="${FRONTEND_REPO:-ghcr.io/fran981259/portal-cerrado-frontend}"
BACKEND_IMAGE_LATEST="${BACKEND_REPO}:latest"
FRONTEND_IMAGE_LATEST="${FRONTEND_REPO}:latest"
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://portal_cerrado:8000}"
NEXT_PUBLIC_SITE_URL="${NEXT_PUBLIC_SITE_URL}"

echo "== Portal Cerrado — Update 1-clique =="
echo "[1/5] git pull"
git pull --ff-only

IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short=12 HEAD)}"
BACKEND_IMAGE_RELEASE="${BACKEND_REPO}:${IMAGE_TAG}"
FRONTEND_IMAGE_RELEASE="${FRONTEND_REPO}:${IMAGE_TAG}"

if [ "$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || echo inactive)" = "active" ]; then
  echo "[2/5] build backend image"
  docker build -t "$BACKEND_IMAGE_LATEST" -t "$BACKEND_IMAGE_RELEASE" .

  echo "[3/5] build frontend image"
  docker build \
    --build-arg NEXT_PUBLIC_API_URL="$NEXT_PUBLIC_API_URL" \
    --build-arg NEXT_PUBLIC_SITE_URL="$NEXT_PUBLIC_SITE_URL" \
    -t "$FRONTEND_IMAGE_LATEST" \
    -t "$FRONTEND_IMAGE_RELEASE" \
    ./frontend

  echo "[4/5] push images"
  docker push "$BACKEND_IMAGE_LATEST"
  docker push "$BACKEND_IMAGE_RELEASE"
  docker push "$FRONTEND_IMAGE_LATEST"
  docker push "$FRONTEND_IMAGE_RELEASE"

  echo "[5/5] deploy stack"
  BACKEND_IMAGE="$BACKEND_IMAGE_RELEASE" FRONTEND_IMAGE="$FRONTEND_IMAGE_RELEASE" DOCKER_NETWORK_DRIVER=overlay docker stack deploy -c docker-compose.yml "$STACK_NAME" --with-registry-auth

  echo "[6/6] force rolling update"
  docker service update --force --image "$BACKEND_IMAGE_RELEASE" "$STACK_NAME"_portal_cerrado
  docker service update --force --image "$BACKEND_IMAGE_RELEASE" "$STACK_NAME"_celery_worker
  docker service update --force --image "$BACKEND_IMAGE_RELEASE" "$STACK_NAME"_celery_beat
  docker service update --force --image "$BACKEND_IMAGE_RELEASE" "$STACK_NAME"_flower
  docker service update --force --image "$FRONTEND_IMAGE_RELEASE" "$STACK_NAME"_frontend

  docker service ls
else
  echo "[2/5] subir stack local/compose"
  docker compose up -d --build

  echo "[3/5] conferir serviços ativos"
  docker compose ps
fi

echo "== Pronto! =="
echo "Frontend: $NEXT_PUBLIC_SITE_URL"
echo "API:      /health no servico backend"
