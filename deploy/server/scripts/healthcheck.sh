#!/usr/bin/env bash
# Smoke test pós-deploy (Cloudflare Tunnel + Docker).
set -euo pipefail

# Valida a origem local; tráfego público passa pelo tunnel (Cloudflare pode
# bloquear IPs de CI em rotas como /healthz).
CODE=$(curl -sk --max-time 15 -o /dev/null -w '%{http_code}' "http://127.0.0.1:8080/healthz")
echo "healthz HTTP $CODE (localhost:8080)"
echo "$CODE" | grep -qE '^(200|301|302)$'

systemctl is-active --quiet nginx
systemctl is-active --quiet cloudflared
systemctl is-active --quiet redis-server
systemctl is-active --quiet postgresql
docker ps --format '{{.Names}}' | grep -qx pdt-web

echo "ok"
