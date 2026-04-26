#!/usr/bin/env bash
# One-shot na EC2: instala Docker + plugin compose (Ubuntu 24.04+).
# Rode como root via SSM se a instância existente foi provisionada sem Docker.
# Depois: usermod -aG docker deploy; reinicie sessão SSM/SSH do usuário deploy.
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl docker.io docker-compose-v2
systemctl enable --now docker
usermod -aG docker deploy || true
docker --version
docker compose version
