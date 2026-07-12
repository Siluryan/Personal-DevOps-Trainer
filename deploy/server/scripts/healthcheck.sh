#!/usr/bin/env bash
# Smoke test pós-deploy (Cloudflare Tunnel + Docker).
set -euo pipefail

DOMAIN="${1:-localhost}"

CODE=$(curl -sk --max-time 15 -o /dev/null -w '%{http_code}' "https://$DOMAIN/healthz")
echo "healthz HTTP $CODE"
echo "$CODE" | grep -qE '^(200|301|302)$'

systemctl is-active --quiet nginx
systemctl is-active --quiet cloudflared
systemctl is-active --quiet redis-server
systemctl is-active --quiet postgresql
docker ps --format '{{.Names}}' | grep -qx pdt-web

echo "ok"
