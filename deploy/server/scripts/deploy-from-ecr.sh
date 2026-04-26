#!/usr/bin/env bash
# Deploy a partir de imagem no ECR (rede do host, Postgres/Redis no SO).
# Chamado via SSM apos o build no GitHub Actions.
# $1 = URI completa da imagem (ex: ...amazonaws.com/pdt/web:sha)
# $2 = commit (apenas log; o workflow ja fez git reset na mesma ref)
# $3 = regiao AWS (ex: us-east-1)
#
# Idempotente e auto-curativo:
#  - cria /opt/pdt/pdt.env se faltar (lendo SSM, igual ao user_data),
#  - instala/arranca Postgres + Redis se faltarem,
#  - cria role/db pdt e ALTER USER com a senha do SSM,
#  - so depois faz pull/up da imagem e migrate/collectstatic.
# Variaveis opcionais: PDT_PROJECT_NAME (pdt), PDT_ENVIRONMENT (prod),
# PDT_BACKUP_BUCKET (fallback se o SSM /.../backup_bucket nao existir).
set -euxo pipefail

IMAGE_URI="${1:?uri da imagem}"
GIT_REF="${2:?commit}"
AWS_REGION_ARG="${3:-us-east-1}"
export AWS_DEFAULT_REGION="${AWS_REGION_ARG}"
export AWS_REGION="${AWS_REGION_ARG}"
export DEBIAN_FRONTEND=noninteractive

PROJECT_NAME="${PDT_PROJECT_NAME:-pdt}"
ENVIRONMENT_NAME="${PDT_ENVIRONMENT:-prod}"
APP_USER=deploy
APP_DIR=/opt/pdt
ENV_FILE=$APP_DIR/pdt.env
REPO_DIR=$APP_DIR/app
PDT_DIR=$REPO_DIR/pdt
COMPOSE_FILE=$PDT_DIR/docker-compose.prod.yml
SCRIPT_NAME="pdt-ecr-$(basename "$IMAGE_URI" | tr ':/' '-')"
logger -t "$SCRIPT_NAME" "deploy ECR: imagem=$IMAGE_URI ref=$GIT_REF"

# Le um parametro do SSM (com ou sem decifragem); imprime vazio se nao existir.
ssm_get() {
  local name="$1" with_dec="${2:-no}"
  if [ "$with_dec" = "yes" ]; then
    aws ssm get-parameter --with-decryption --name "$name" \
      --query Parameter.Value --output text 2>/dev/null || true
  else
    aws ssm get-parameter --name "$name" \
      --query Parameter.Value --output text 2>/dev/null || true
  fi
}

# Garante /opt/pdt/pdt.env (mesmo conteudo que o user_data do Terraform geraria).
ensure_pdt_env() {
  local PN="$PROJECT_NAME" PE="$ENVIRONMENT_NAME"
  POSTGRES_PASSWORD_VAL=$(ssm_get "/$PN/$PE/postgres/password" yes)
  if [ -z "$POSTGRES_PASSWORD_VAL" ]; then
    echo "::error::SSM /$PN/$PE/postgres/password vazio; abortando" >&2
    exit 1
  fi
  if [ -f "$ENV_FILE" ]; then
    return 0
  fi
  local SK DOM BUCK
  SK=$(ssm_get "/$PN/$PE/django/secret_key" yes)
  DOM=$(ssm_get "/$PN/$PE/domain_name")
  BUCK=$(ssm_get "/$PN/$PE/backup_bucket")
  BUCK=${BUCK:-${PDT_BACKUP_BUCKET:-}}
  if [ -z "$BUCK" ]; then
    logger -t "$SCRIPT_NAME" "aviso: backup_bucket nao lido; cron de backup ficara sem destino"
  fi
  install -d -m 0755 "$APP_DIR"
  umask 077
  cat >"$ENV_FILE" <<ENVEOF
DJANGO_SECRET_KEY=$SK
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$DOM,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS_EXTRA=https://$DOM
POSTGRES_DB=pdt
POSTGRES_USER=pdt
POSTGRES_PASSWORD=$POSTGRES_PASSWORD_VAL
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/0
DJANGO_BACKUP_BUCKET=$BUCK
ENVEOF
  chown "$APP_USER":"$APP_USER" "$ENV_FILE" 2>/dev/null || chown root:root "$ENV_FILE"
  chmod 640 "$ENV_FILE"
  logger -t "$SCRIPT_NAME" "criado $ENV_FILE a partir de SSM"
}

apt_install_if_missing() {
  local pkgs=()
  for p in "$@"; do
    dpkg -s "$p" >/dev/null 2>&1 || pkgs+=("$p")
  done
  if [ "${#pkgs[@]}" -gt 0 ]; then
    logger -t "$SCRIPT_NAME" "apt install: ${pkgs[*]}"
    apt-get update -y
    apt-get install -y --no-install-recommends "${pkgs[@]}"
  fi
}

postgres_listening_on_localhost() {
  if command -v pg_isready >/dev/null 2>&1; then
    pg_isready -h 127.0.0.1 -p 5432 -q 2>/dev/null
    return
  fi
  ( echo >/dev/tcp/127.0.0.1/5432 ) 2>/dev/null
}

start_postgres_units() {
  systemctl start postgresql 2>/dev/null || true
  if [ -d /etc/postgresql ]; then
    shopt -s nullglob
    for d in /etc/postgresql/*/main; do
      [ -d "$d" ] || continue
      v="${d#"/etc/postgresql/"}"
      v="${v%%/*}"
      systemctl start "postgresql@${v}-main" 2>/dev/null || true
      command -v pg_ctlcluster >/dev/null 2>&1 \
        && pg_ctlcluster "$v" main start 2>/dev/null || true
    done
    shopt -u nullglob
  fi
}

wait_postgres_5432() {
  local w=0 max="${1:-90}"
  while [ "$w" -lt "$max" ]; do
    if postgres_listening_on_localhost; then
      logger -t "$SCRIPT_NAME" "Postgres OK em 127.0.0.1:5432"
      return 0
    fi
    w=$((w + 1))
    sleep 1
  done
  return 1
}

ensure_postgres_db_and_user() {
  local pwd="$1"
  sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='pdt'" 2>/dev/null | grep -q 1 \
    || sudo -u postgres psql -c "CREATE USER pdt WITH PASSWORD '$pwd';"
  sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='pdt'" 2>/dev/null | grep -q 1 \
    || sudo -u postgres createdb -O pdt pdt
  sudo -u postgres psql -c "ALTER USER pdt WITH PASSWORD '$pwd';" >/dev/null
}

ensure_postgres() {
  apt_install_if_missing postgresql postgresql-contrib
  start_postgres_units
  if ! wait_postgres_5432 90; then
    echo "::error::Postgres nao responde em 127.0.0.1:5432 apos 90s" >&2
    systemctl --no-pager -l status postgresql 2>&1 | head -40 || true
    (command -v ss >/dev/null && ss -lntp 2>/dev/null | grep 5432) || true
    (command -v pg_lsclusters >/dev/null && pg_lsclusters) || true
    exit 1
  fi
  ensure_postgres_db_and_user "$POSTGRES_PASSWORD_VAL"
}

ensure_redis() {
  apt_install_if_missing redis-server
  if [ -f /etc/redis/redis.conf ]; then
    sed -i 's/^bind .*/bind 127.0.0.1 -::1/' /etc/redis/redis.conf || true
    sed -i 's/^protected-mode .*/protected-mode yes/' /etc/redis/redis.conf || true
    grep -q '^maxmemory ' /etc/redis/redis.conf || echo 'maxmemory 96mb' >>/etc/redis/redis.conf
    grep -q '^maxmemory-policy ' /etc/redis/redis.conf || echo 'maxmemory-policy allkeys-lru' >>/etc/redis/redis.conf
  fi
  systemctl enable redis-server 2>/dev/null || true
  systemctl start redis-server 2>/dev/null || systemctl start redis 2>/dev/null || true
}

# Coloca o nginx HTTP-only no ar a partir do template (sem o bloco 443) para
# o certbot conseguir o desafio HTTP-01. Idempotente.
write_nginx_http_only() {
  local domain="$1" template="$REPO_DIR/deploy/server/nginx/pdt.conf.tpl"
  local out=/etc/nginx/sites-available/pdt.conf
  if [ ! -f "$template" ]; then
    echo "::error::template nginx ausente em $template" >&2
    exit 1
  fi
  install -d -m 0755 /var/www/html /etc/nginx/snippets
  install -m 0644 "$REPO_DIR/deploy/server/nginx/snippets/pdt_proxy.conf" \
    /etc/nginx/snippets/pdt_proxy.conf
  python3 - "$template" "$domain" "$out" <<'PYEOF'
import re, sys
src = open(sys.argv[1]).read().replace("__DOMAIN__", sys.argv[2])
out = []
depth = 0
seen = 0
for line in src.splitlines():
    stripped = line.strip()
    if re.match(r"^server\s*\{", stripped):
        seen += 1
        depth = 1
        if seen == 2:
            continue
        out.append(line)
        continue
    if depth and seen == 2:
        if "{" in stripped:
            depth += 1
        if "}" in stripped:
            depth -= 1
            if depth == 0:
                continue
        continue
    out.append(line)
open(sys.argv[3], "w").write("\n".join(out) + "\n")
PYEOF
  ln -sf /etc/nginx/sites-available/pdt.conf /etc/nginx/sites-enabled/pdt.conf
  rm -f /etc/nginx/sites-enabled/default
  nginx -t
  systemctl enable --now nginx
  systemctl reload nginx
}

ensure_nginx_tls() {
  local domain="$1" email="$2"
  apt_install_if_missing nginx certbot python3-certbot-nginx
  if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q 'Status: active'; then
    ufw allow 80/tcp || true
    ufw allow 443/tcp || true
  fi

  if [ ! -d "/etc/letsencrypt/live/$domain" ]; then
    write_nginx_http_only "$domain"
    if [ -z "$email" ]; then
      logger -t "$SCRIPT_NAME" "aviso: letsencrypt_email vazio; pulando emissao do cert (DNS+email exigidos)"
    else
      certbot --nginx -d "$domain" \
        --non-interactive --agree-tos -m "$email" --redirect \
        || logger -t "$SCRIPT_NAME" "certbot inicial falhou (DNS apontando para esta EC2?)"
    fi
  else
    install -d -m 0755 /etc/nginx/snippets
    install -m 0644 "$REPO_DIR/deploy/server/nginx/snippets/pdt_proxy.conf" \
      /etc/nginx/snippets/pdt_proxy.conf
    nginx -t && systemctl reload nginx 2>/dev/null || systemctl restart nginx 2>/dev/null || true
    systemctl enable --now nginx 2>/dev/null || true
  fi
  systemctl enable --now certbot.timer 2>/dev/null || true
}

ensure_pdt_env
ensure_postgres
ensure_redis

# Login no ECR (instancia com role que permite ecr pull).
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

# Migracao e estaticos dentro do conteiner (mesma imagem usada no run).
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py migrate --noinput
docker compose -f "$COMPOSE_FILE" exec -T web python manage.py collectstatic --noinput

# Nginx le /static e /media (www-data): garante leitura.
chmod -R a+rX /opt/pdt/app/pdt/staticfiles /opt/pdt/app/pdt/media 2>/dev/null || true

# Publica em 80/443 via nginx + Let's Encrypt (idempotente, requer DNS apontando aqui).
DOMAIN_VAL=$(ssm_get "/$PROJECT_NAME/$ENVIRONMENT_NAME/domain_name")
LE_EMAIL_VAL=$(ssm_get "/$PROJECT_NAME/$ENVIRONMENT_NAME/letsencrypt_email")
if [ -n "$DOMAIN_VAL" ]; then
  ensure_nginx_tls "$DOMAIN_VAL" "$LE_EMAIL_VAL"
fi

# Mantem a copia em /opt/pdt/scripts atualizada (idempotente).
install -d -m 0755 /opt/pdt/scripts
if [ -f "$REPO_DIR/deploy/server/scripts/deploy-from-ecr.sh" ]; then
  install -m 0755 "$REPO_DIR/deploy/server/scripts/deploy-from-ecr.sh" /opt/pdt/scripts/deploy-from-ecr.sh
fi

logger -t "$SCRIPT_NAME" "deploy concluido"
exit 0
