#!/usr/bin/env bash
# Cria /opt/pdt, garante o utilizador "deploy" e clona o repositório do GitHub
# em /opt/pdt/app (caminho esperado pelo user_data, deploy-from-ecr e o workflow GHA).
#
# Padrão (se não passar nada): Siluryan/Personal-DevOps-Trainer
#   sudo bash clone-pdt-app-repo.sh
#
# Outro repo (repo público):
#   sudo bash clone-pdt-app-repo.sh DONO/repositorio
#   sudo GITHUB_REPO=DONO/repositorio bash clone-pdt-app-repo.sh
#
# Repositório privado: token com leitura ao repositório (não fazer commit do token)
#   export GITHUB_TOKEN=ghp_...
#   sudo -E GITHUB_REPO=DONO/repositorio bash clone-pdt-app-repo.sh
#
# Depois: confirme /opt/pdt/pdt.env (bootstrap do Terraform) e Docker se usar ECR.
set -euo pipefail

# https://github.com/Siluryan/Personal-DevOps-Trainer
REPO_SLUG="${GITHUB_REPO:-${1:-Siluryan/Personal-DevOps-Trainer}}"

if [ "${EUID:-0}" -ne 0 ]; then
  echo "Execute como root: sudo $0 $REPO_SLUG" >&2
  exit 1
fi

APP_USER=deploy
APP_DIR=/opt/pdt
APP_REPO_DIR=$APP_DIR/app

if ! id -u "$APP_USER" &>/dev/null; then
  adduser --disabled-password --gecos '' "$APP_USER"
fi
loginctl enable-linger "$APP_USER" 2>/dev/null || true

mkdir -p "$APP_DIR"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# URL: HTTPS simples, ou com token (repo privado)
if [ -n "${GITHUB_TOKEN:-}" ]; then
  CLONE_URL="https://${GITHUB_TOKEN}@github.com/${REPO_SLUG}.git"
else
  CLONE_URL="https://github.com/${REPO_SLUG}.git"
fi

sudo -u "$APP_USER" -H bash <<EOSU
set -euo pipefail
cd $APP_DIR
if [ -d $APP_REPO_DIR/.git ]; then
  echo "Repositório já existe em $APP_REPO_DIR; a atualizar..."
  git -C $APP_REPO_DIR remote set-url origin "https://github.com/${REPO_SLUG}.git" || true
  git -C $APP_REPO_DIR fetch origin
  git -C $APP_REPO_DIR pull --ff-only || {
    git -C $APP_REPO_DIR fetch origin
    git -C $APP_REPO_DIR reset --hard origin/main || git -C $APP_REPO_DIR reset --hard origin/master
  }
else
  git clone --depth 1 "$CLONE_URL" app
fi
cd $APP_REPO_DIR
git config --global --add safe.directory $APP_REPO_DIR
EOSU

# Restaurar remote sem token (evita deixar credencial no config após clone com token)
if [ -n "${GITHUB_TOKEN:-}" ]; then
  sudo -u "$APP_USER" -H git -C "$APP_REPO_DIR" remote set-url origin "https://github.com/${REPO_SLUG}.git"
fi

echo ""
echo "OK: código em $APP_REPO_DIR"
ls -la "$APP_REPO_DIR" | head
echo ""
echo "Próximos passos: /opt/pdt/pdt.env (SSM/Parameter Store se for stack Terraform);"
echo "  Docker/ECR: prepare-docker-compose-prereq.sh; deploy: workflow ou deploy-from-ecr.sh"
