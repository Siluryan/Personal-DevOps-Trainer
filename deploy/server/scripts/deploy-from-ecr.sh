#!/usr/bin/env bash
# Deploy a partir de imagem no ECR (rede do host, Postgres/Redis no SO).
# Chamado via SSM após o build no GitHub Actions.
# $1 = URI completa da imagem (ex: ...amazonaws.com/pdt/web:sha)
# $2 = commit (apenas log; o workflow já fez git reset na mesma ref)
# $3 = região AWS (ex: us-east-1)
# Se /opt/pdt/pdt.env faltar (bootstrap parcial, clone manual, etc.),
# reconstrui a partir dos mesmos parâmetros SSM que o user_data (Terraform).
# Opcional: PDT_BACKUP_BUCKET se o SSM /.../backup_bucket ainda não existir
# (stacks antigos, antes de terraform apply com o parâmetro novo).
set -euxo pipefail

IMAGE_URI="${1:?uri da imagem}"
GIT_REF="${2:?commit}"
AWS_REGION_ARG="${3:-us-east-1}"
export AWS_DEFAULT_REGION="${AWS_REGION_ARG}"
export AWS_REGION="${AWS_REGION_ARG}"

APP_USER=deploy
APP_DIR=/opt/pdt
ENV_FILE=$APP_DIR/pdt.env
REPO_DIR=$APP_DIR/app
PDT_DIR=$REPO_DIR/pdt
COMPOSE_FILE=$PDT_DIR/docker-compose.prod.yml
SCRIPT_NAME="pdt-ecr-$(basename "$IMAGE_URI" | tr ':/' '-')"
logger -t "$SCRIPT_NAME" "deploy ECR: imagem=$IMAGE_URI ref=$GIT_REF"

ensure_pdt_env() {
  if [ -f "$ENV_FILE" ]; then
    return 0
  fi
  local PN="${PDT_PROJECT_NAME:-pdt}"
  local PE="${PDT_ENVIRONMENT:-prod}"
  local SK PG DOM BUCK
  SK=$(aws ssm get-parameter --with-decryption --name "/$PN/$PE/django/secret_key" \
    --query Parameter.Value --output text)
  PG=$(aws ssm get-parameter --with-decryption --name "/$PN/$PE/postgres/password" \
    --query Parameter.Value --output text)
  DOM=$(aws ssm get-parameter --name "/$PN/$PE/domain_name" --query Parameter.Value --output text)
  BUCK=$(aws ssm get-parameter --name "/$PN/$PE/backup_bucket" \
    --query Parameter.Value --output text 2>/dev/null || true)
  BUCK=${BUCK:-${PDT_BACKUP_BUCKET:-}}
  if [ -z "$BUCK" ]; then
    logger -t "$SCRIPT_NAME" "aviso: backup_bucket nao lido (SSM /$PN/$PE/backup_bucket ou PDT_BACKUP_BUCKET). DJANGO_BACKUP_BUCKET vazio; corrija antes do cron de backup"
  fi
  umask 077
  install -d -m 0755 "$APP_DIR"
  cat >"$ENV_FILE" <<ENVEOF
DJANGO_SECRET_KEY=$SK
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$DOM,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS_EXTRA=https://$DOM
POSTGRES_DB=pdt
POSTGRES_USER=pdt
POSTGRES_PASSWORD=$PG
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/0
DJANGO_BACKUP_BUCKET=$BUCK
ENVEOF
  chown "$APP_USER":"$APP_USER" "$ENV_FILE" 2>/dev/null || chown root:root "$ENV_FILE"
  chmod 640 "$ENV_FILE"
  logger -t "$SCRIPT_NAME" "criado $ENV_FILE a partir de SSM"
}

ensure_pdt_env

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
