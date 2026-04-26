#!/usr/bin/env bash
# Backup diário: pg_dump + media -> S3, com tag de retenção.
# Acionado pelo SSM Association definido em ssm_patching.tf.
set -euxo pipefail

ENV_FILE=/opt/pdt/pdt.env
APP_DIR=/opt/pdt/app/pdt
TS=$(date -u +%Y%m%dT%H%M%SZ)
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

set -a; . "$ENV_FILE"; set +a

BUCKET="${DJANGO_BACKUP_BUCKET:?DJANGO_BACKUP_BUCKET ausente em $ENV_FILE}"

# 1. dump do Postgres
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
  -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \
  -U "$POSTGRES_USER" "$POSTGRES_DB" \
  -Fc \
  -f "$TMPDIR/pdt_${TS}.dump"

# 2. tarball de media
if [ -d "$APP_DIR/media" ] && [ -n "$(ls -A "$APP_DIR/media" 2>/dev/null)" ]; then
  tar -czf "$TMPDIR/media_${TS}.tar.gz" -C "$APP_DIR" media
fi

# 3. envia para S3
aws s3 cp "$TMPDIR/pdt_${TS}.dump" "s3://$BUCKET/db/pdt_${TS}.dump"
[ -f "$TMPDIR/media_${TS}.tar.gz" ] && \
  aws s3 cp "$TMPDIR/media_${TS}.tar.gz" "s3://$BUCKET/media/media_${TS}.tar.gz"

logger -t pdt-backup "ok ts=$TS bucket=$BUCKET"
