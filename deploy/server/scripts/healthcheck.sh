#!/usr/bin/env bash
# Smoke test pós-deploy. Sai com código não-zero se algo estiver fora do ar.
set -euo pipefail

DOMAIN="${1:-localhost}"

curl --fail --silent --show-error --max-time 10 \
  -o /dev/null -w '%{http_code}\n' \
  "https://$DOMAIN/healthz" \
  | grep -E '^(200|301|302)$'

systemctl is-active --quiet pdt-daphne
systemctl is-active --quiet nginx
systemctl is-active --quiet redis-server
systemctl is-active --quiet postgresql

echo "ok"
