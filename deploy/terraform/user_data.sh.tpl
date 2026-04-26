#!/bin/bash
# ============================================================================
# user_data: prepara a EC2 t3.micro Ubuntu 24.04 para rodar o PDT (Django + 
# Channels). Idempotente o suficiente para reexecutar via `cloud-init clean`.
#
# Pilares:
#   1) hardening do sistema (SSH, UFW, fail2ban, sysctl, auditd, automatic
#      security updates),
#   2) swap de 2GB (a t3.micro tem só 1GB de RAM),
#   3) instalação do runtime (python, postgres, redis, nginx, certbot),
#   4) usuário `deploy` sem sudo,
#   5) systemd unit do app, nginx + Let's Encrypt e cron de backup.
# ============================================================================
set -euxo pipefail

PROJECT="${project_name}"
ENVIRONMENT="${environment}"
AWS_REGION="${aws_region}"
DOMAIN_NAME="${domain_name}"
LE_EMAIL="${letsencrypt_email}"
GITHUB_REPO="${github_repo}"
BACKUP_BUCKET="${backup_bucket}"
SSM_DJANGO_SECRET="${ssm_django_secret}"
SSM_POSTGRES_PWD="${ssm_postgres_pwd}"

APP_USER=deploy
APP_DIR=/opt/pdt
APP_REPO_DIR=$APP_DIR/app
ENV_FILE=$APP_DIR/pdt.env
LOG_TAG="pdt-userdata"

logger -t "$LOG_TAG" "iniciando user_data para $PROJECT/$ENVIRONMENT"

export DEBIAN_FRONTEND=noninteractive

# ─── 1. Pacotes base ────────────────────────────────────────────────────────
apt-get update
apt-get -y dist-upgrade
apt-get install -y --no-install-recommends \
  ca-certificates curl gnupg jq unzip git \
  ufw fail2ban auditd unattended-upgrades apt-listchanges needrestart \
  apparmor apparmor-utils \
  python3 python3-venv python3-pip python3-dev build-essential \
  libpq-dev pkg-config libffi-dev libssl-dev \
  postgresql postgresql-contrib redis-server \
  nginx certbot python3-certbot-nginx \
  docker.io docker-compose-v2 \
  logrotate cron rsync sqlite3

# Ubuntu 24.04: pacote apt "awscli" costuma nao existir; instala AWS CLI v2 se faltar.
if ! command -v aws &>/dev/null; then
  ARCH=$(uname -m)
  case "$ARCH" in
    x86_64)  Z=awscli-exe-linux-x86_64.zip ;;
    aarch64) Z=awscli-exe-linux-aarch64.zip ;;
    *)       Z=awscli-exe-linux-x86_64.zip ;;
  esac
  curl -sS "https://awscli.amazonaws.com/$${Z}" -o /tmp/awscliv2.zip
  unzip -q -o /tmp/awscliv2.zip -d /tmp
  /tmp/aws/install -i /usr/local/aws-cli -b /usr/local/bin
  rm -rf /tmp/aws /tmp/awscliv2.zip
fi

systemctl enable --now ssm-agent || systemctl enable --now amazon-ssm-agent || true
systemctl enable --now docker || true
usermod -aG docker $APP_USER 2>/dev/null || true

# ─── 2. Swap de 2GB (t3.micro = 1GB RAM) ────────────────────────────────────
if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
  sysctl -w vm.swappiness=10
  echo 'vm.swappiness=10' > /etc/sysctl.d/99-pdt-swap.conf
fi

# ─── 3. Hardening de kernel ────────────────────────────────────────────────
cat >/etc/sysctl.d/99-pdt-hardening.conf <<'EOF'
# Rede
net.ipv4.conf.all.rp_filter=1
net.ipv4.conf.default.rp_filter=1
net.ipv4.conf.all.accept_redirects=0
net.ipv4.conf.default.accept_redirects=0
net.ipv4.conf.all.secure_redirects=0
net.ipv4.conf.default.secure_redirects=0
net.ipv4.conf.all.send_redirects=0
net.ipv4.conf.default.send_redirects=0
net.ipv4.conf.all.accept_source_route=0
net.ipv4.conf.default.accept_source_route=0
net.ipv4.conf.all.log_martians=1
net.ipv4.icmp_echo_ignore_broadcasts=1
net.ipv4.icmp_ignore_bogus_error_responses=1
net.ipv4.tcp_syncookies=1
net.ipv6.conf.all.accept_redirects=0
net.ipv6.conf.default.accept_redirects=0
# Filesystem / processo
fs.protected_hardlinks=1
fs.protected_symlinks=1
fs.protected_fifos=2
fs.protected_regular=2
fs.suid_dumpable=0
kernel.dmesg_restrict=1
kernel.kptr_restrict=2
kernel.unprivileged_bpf_disabled=1
kernel.yama.ptrace_scope=2
kernel.randomize_va_space=2
EOF
sysctl --system

# ─── 4. SSH hardening ──────────────────────────────────────────────────────
cat >/etc/ssh/sshd_config.d/00-pdt-hardening.conf <<'EOF'
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
ChallengeResponseAuthentication no
KbdInteractiveAuthentication no
UsePAM yes
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
PermitEmptyPasswords no
MaxAuthTries 3
LoginGraceTime 30
ClientAliveInterval 300
ClientAliveCountMax 2
Banner /etc/issue.net
EOF
cat >/etc/issue.net <<'EOF'
+----------------------------------------------------------------+
|  Acesso restrito. Toda atividade é registrada e monitorada.    |
+----------------------------------------------------------------+
EOF
systemctl restart ssh

# ─── 5. UFW (defesa em profundidade vs. SG) ────────────────────────────────
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'ssh'
ufw allow 80/tcp comment 'http'
ufw allow 443/tcp comment 'https'
ufw logging low
ufw --force enable

# ─── 6. fail2ban (sshd + nginx) ────────────────────────────────────────────
cat >/etc/fail2ban/jail.d/pdt.conf <<'EOF'
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 5
backend  = systemd

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-bad-request]
enabled = true
filter  = nginx-bad-request
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
filter  = nginx-botsearch
logpath = /var/log/nginx/access.log
maxretry = 5
EOF
cat >/etc/fail2ban/filter.d/nginx-bad-request.conf <<'EOF'
[Definition]
failregex = ^<HOST>.*"(GET|POST|HEAD).*" (400|408|444) .*$
ignoreregex =
EOF
systemctl enable --now fail2ban

# ─── 7. Atualizações automáticas de segurança ──────────────────────────────
cat >/etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Download-Upgradeable-Packages "1";
EOF
cat >/etc/apt/apt.conf.d/50unattended-upgrades.local <<'EOF'
Unattended-Upgrade::Allowed-Origins {
  "$${distro_id}:$${distro_codename}-security";
  "$${distro_id}ESMApps:$${distro_codename}-apps-security";
  "$${distro_id}ESM:$${distro_codename}-infra-security";
};
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "04:30";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
EOF
systemctl enable --now unattended-upgrades

# ─── 8. auditd (regras mínimas para auditoria de acesso) ───────────────────
cat >/etc/audit/rules.d/pdt.rules <<'EOF'
-w /etc/passwd  -p wa -k passwd_changes
-w /etc/shadow  -p wa -k shadow_changes
-w /etc/sudoers -p wa -k sudoers_changes
-w /var/log/auth.log -p wa -k auth_log
-w /etc/ssh/sshd_config -p wa -k sshd_config
-w /opt/pdt -p wa -k pdt_changes
EOF
augenrules --load
systemctl enable --now auditd

# ─── 9. Usuário deploy (sem sudo) ─────────────────────────────────────────
if ! id -u $APP_USER >/dev/null 2>&1; then
  adduser --disabled-password --gecos '' $APP_USER
fi
loginctl enable-linger $APP_USER || true
mkdir -p $APP_DIR
chown -R $APP_USER:$APP_USER $APP_DIR

# ─── 10. PostgreSQL local + tuning para 1GB RAM ───────────────────────────
PG_VERSION=$(ls /etc/postgresql/ | head -n1)
PG_CONF=/etc/postgresql/$PG_VERSION/main/postgresql.conf
cat >>$PG_CONF <<'EOF'

# tuning t3.micro (1GB RAM)
shared_buffers = 128MB
work_mem = 4MB
maintenance_work_mem = 32MB
effective_cache_size = 512MB
max_connections = 30
wal_compression = on
EOF
systemctl restart postgresql

POSTGRES_PASSWORD=$(aws ssm get-parameter --with-decryption \
  --name "$SSM_POSTGRES_PWD" --region "$AWS_REGION" \
  --query 'Parameter.Value' --output text)
DJANGO_SECRET_KEY=$(aws ssm get-parameter --with-decryption \
  --name "$SSM_DJANGO_SECRET" --region "$AWS_REGION" \
  --query 'Parameter.Value' --output text)

sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='pdt'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE USER pdt WITH PASSWORD '$POSTGRES_PASSWORD';"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='pdt'" | grep -q 1 \
  || sudo -u postgres createdb -O pdt pdt
sudo -u postgres psql -c "ALTER USER pdt WITH PASSWORD '$POSTGRES_PASSWORD';"

# ─── 11. Redis hardening (bind local, sem persistência) ───────────────────
sed -i 's/^bind .*/bind 127.0.0.1 -::1/' /etc/redis/redis.conf
sed -i 's/^protected-mode .*/protected-mode yes/' /etc/redis/redis.conf
sed -i 's/^# maxmemory .*/maxmemory 96mb/' /etc/redis/redis.conf
grep -q '^maxmemory ' /etc/redis/redis.conf || echo 'maxmemory 96mb' >> /etc/redis/redis.conf
grep -q '^maxmemory-policy ' /etc/redis/redis.conf \
  || echo 'maxmemory-policy allkeys-lru' >> /etc/redis/redis.conf
systemctl restart redis-server
systemctl enable redis-server

# ─── 12. Clonar repositório como usuário deploy ───────────────────────────
sudo -u $APP_USER -H bash <<EOSU
set -euxo pipefail
cd $APP_DIR
if [ ! -d $APP_REPO_DIR/.git ]; then
  git clone --depth 1 https://github.com/$GITHUB_REPO.git app
fi
cd $APP_REPO_DIR
git config --global --add safe.directory $APP_REPO_DIR
EOSU

# ─── 13. .env do app ──────────────────────────────────────────────────────
cat >$ENV_FILE <<EOF
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$DOMAIN_NAME,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS_EXTRA=https://$DOMAIN_NAME
POSTGRES_DB=pdt
POSTGRES_USER=pdt
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/0
DJANGO_BACKUP_BUCKET=$BACKUP_BUCKET
EOF
chown $APP_USER:$APP_USER $ENV_FILE
chmod 640 $ENV_FILE

# ─── 14. Setup do venv + migrate + collectstatic ──────────────────────────
sudo -u $APP_USER -H bash <<'EOSU'
set -euxo pipefail
cd /opt/pdt/app/pdt
python3 -m venv /opt/pdt/venv
. /opt/pdt/venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
set -a; . /opt/pdt/pdt.env; set +a
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_topics || true
python manage.py seed_admission_test || true
python manage.py seed_interviews || true
EOSU

# ─── 15. systemd unit do daphne ───────────────────────────────────────────
install -m 0644 /opt/pdt/app/deploy/server/systemd/pdt-daphne.service \
  /etc/systemd/system/pdt-daphne.service
systemctl daemon-reload
systemctl enable --now pdt-daphne.service

# ─── 16. nginx + Let's Encrypt ────────────────────────────────────────────
NGINX_CONF=/etc/nginx/sites-available/pdt.conf
sed "s|__DOMAIN__|$DOMAIN_NAME|g" \
  /opt/pdt/app/deploy/server/nginx/pdt.conf.tpl >$NGINX_CONF
ln -sf $NGINX_CONF /etc/nginx/sites-enabled/pdt.conf
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Emite certificado se ainda não existe; o systemd timer do certbot cuida da renovação.
if [ ! -d /etc/letsencrypt/live/$DOMAIN_NAME ]; then
  certbot --nginx \
    -d $DOMAIN_NAME \
    --non-interactive --agree-tos -m "$LE_EMAIL" \
    --redirect || logger -t "$LOG_TAG" "certbot inicial falhou; rode manualmente após o DNS apontar"
fi
systemctl enable --now certbot.timer
systemctl enable --now snap.certbot.renew.timer 2>/dev/null || true

# ─── 17. Scripts utilitários (backup, deploy) ────────────────────────────
install -m 0755 /opt/pdt/app/deploy/server/scripts/backup.sh /opt/pdt/scripts/backup.sh 2>/dev/null \
  || { mkdir -p /opt/pdt/scripts; cp /opt/pdt/app/deploy/server/scripts/backup.sh /opt/pdt/scripts/backup.sh; chmod 0755 /opt/pdt/scripts/backup.sh; }
install -m 0755 /opt/pdt/app/deploy/server/scripts/deploy.sh /opt/pdt/scripts/deploy.sh 2>/dev/null \
  || { cp /opt/pdt/app/deploy/server/scripts/deploy.sh /opt/pdt/scripts/deploy.sh; chmod 0755 /opt/pdt/scripts/deploy.sh; }
install -m 0755 /opt/pdt/app/deploy/server/scripts/deploy-from-ecr.sh /opt/pdt/scripts/deploy-from-ecr.sh 2>/dev/null \
  || { cp /opt/pdt/app/deploy/server/scripts/deploy-from-ecr.sh /opt/pdt/scripts/deploy-from-ecr.sh; chmod 0755 /opt/pdt/scripts/deploy-from-ecr.sh; }
chown -R $APP_USER:$APP_USER /opt/pdt/scripts

# ─── 18. logrotate da app ────────────────────────────────────────────────
cat >/etc/logrotate.d/pdt <<'EOF'
/var/log/pdt/*.log {
  weekly
  rotate 8
  compress
  delaycompress
  missingok
  notifempty
  copytruncate
}
EOF
mkdir -p /var/log/pdt
chown $APP_USER:$APP_USER /var/log/pdt

logger -t "$LOG_TAG" "user_data concluído para $PROJECT/$ENVIRONMENT"
