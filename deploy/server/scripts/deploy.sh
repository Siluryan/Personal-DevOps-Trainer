#!/usr/bin/env bash
# Deploy in-place: chamado pelo SSM SendCommand a partir do GitHub Actions.
# Idempotente: roda como root (SSM); puxa código como `deploy`, instala deps,
# aplica migrations, coleta estáticos e reinicia o daphne.
set -euxo pipefail

APP_USER=deploy
APP_DIR=/opt/pdt
APP_REPO_DIR=$APP_DIR/app
ENV_FILE=$APP_DIR/pdt.env
BRANCH="${1:-main}"

logger -t pdt-deploy "iniciando deploy branch=$BRANCH"

sudo -u $APP_USER -H bash <<EOSU
set -euxo pipefail
cd $APP_REPO_DIR
git fetch origin
git checkout $BRANCH
git reset --hard origin/$BRANCH
cd $APP_REPO_DIR/pdt
. /opt/pdt/venv/bin/activate
pip install -r requirements.txt
set -a; . $ENV_FILE; set +a
python manage.py migrate --noinput
python manage.py collectstatic --noinput
EOSU

# Atualiza configs do servidor (nginx + systemd) caso tenham mudado.
install -m 0644 $APP_REPO_DIR/deploy/server/systemd/pdt-daphne.service \
  /etc/systemd/system/pdt-daphne.service
systemctl daemon-reload

DOMAIN=$(grep -E '^DJANGO_ALLOWED_HOSTS=' "$ENV_FILE" | head -n1 | cut -d= -f2 | cut -d, -f1)
NGINX_CONF=/etc/nginx/sites-available/pdt.conf
sed "s|__DOMAIN__|$DOMAIN|g" \
  $APP_REPO_DIR/deploy/server/nginx/pdt.conf.tpl >$NGINX_CONF
mkdir -p /etc/nginx/snippets
install -m 0644 $APP_REPO_DIR/deploy/server/nginx/snippets/pdt_proxy.conf \
  /etc/nginx/snippets/pdt_proxy.conf
nginx -t

systemctl reload nginx
systemctl restart pdt-daphne

logger -t pdt-deploy "deploy concluído branch=$BRANCH"
