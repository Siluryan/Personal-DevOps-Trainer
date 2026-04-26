#!/usr/bin/env bash
set -euo pipefail

echo ">> Aguardando o banco de dados..."
python <<'PY'
import os, time, sys
import psycopg
host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]
db = os.environ["POSTGRES_DB"]
for i in range(60):
    try:
        psycopg.connect(host=host, port=port, user=user, password=password, dbname=db).close()
        print("Banco respondendo.")
        sys.exit(0)
    except Exception as e:
        print(f"Tentativa {i+1}: {e}")
        time.sleep(1)
print("Timeout esperando o banco")
sys.exit(1)
PY

echo ">> Aplicando migrações..."
python manage.py migrate --noinput

echo ">> Coletando estáticos..."
python manage.py collectstatic --noinput

echo ">> Semeando conteúdo (idempotente)..."
python manage.py seed_topics || true
python manage.py seed_admission_test || true
python manage.py seed_interviews || true

echo ">> Iniciando processo principal: $@"
exec "$@"
