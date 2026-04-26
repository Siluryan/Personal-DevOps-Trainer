#!/usr/bin/env bash
# Deploy a partir de imagem no ECR (rede do host, Postgres/Redis no SO).
# Chamado via SSM após o build no GitHub Actions.
# $1 = URI completa da imagem (ex: ...amazonaws.com/pdt/web:sha)
# $2 = commit (apenas log; o workflow já fez git reset na mesma ref)
# $3 = região AWS (ex: us-east-1)
# Pré-condição: o Git em /opt/pdt/app aponta para o commit de build.
set -euxo pipefail

IMAGE_URI="${1:?uri da imagem}"
GIT_REF="${2:?commit}"
AWS_REGION_ARG="${3:-us-east-1}"
export AWS_DEFAULT_REGION="${AWS_REGION_ARG}"
export AWS_REGION="${AWS_REGION_ARG}"

APP_USER=deploy
APP_DIR=/opt/pdt
REPO_DIR=$APP_DIR/app
PDT_DIR=$REPO_DIR/pdt
COMPOSE_FILE=$PDT_DIR/docker-compose.prod.yml
SCRIPT_NAME="pdt-ecr-$(basename "$IMAGE_URI" | tr ':/' '-')"
logger -t "$SCRIPT_NAME" "deploy ECR: imagem=$IMAGE_URI ref=$GIT_REF"

# Login no ECR (instância com role que permite ecr pull).
ECR_HOST=$(echo "$IMAGE_URI" | cut -d/ -f1)
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ECR_HOST"

export PDT_ECR_IMAGE="$IMAGE_URI"

# Troca o runtime do app de venv/systemd para o container.
systemctl stop pdt-daphne.service 2>/dev/null || true
systemctl disable pdt-daphne.service 2>/dev/null || true

cd "$PDT_DIR"
docker compose -f "$COMPOSE_FILE" pull web
docker compose -f "$COMPOSE_FILE" up -d web

# Migração e estáticos dentro do contêiner (mesma imagem usada no run).
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py migrate --noinput
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py collectstatic --noinput

# Nginx lê /static e /media (www-data): garante leitura (collectstatic no root).
chmod -R a+rX /opt/pdt/app/pdt/staticfiles /opt/pdt/app/pdt/media 2>/dev/null || true

# Instala a cópia usada em /opt/pdt/scripts (idempotente).
if [ -f "$REPO_DIR/deploy/server/scripts/deploy-from-ecr.sh" ]; then
  install -m 0755 "$REPO_DIR/deploy/server/scripts/deploy-from-ecr.sh" /opt/pdt/scripts/deploy-from-ecr.sh
fi

logger -t "$SCRIPT_NAME" "deploy concluído"
exit 0
