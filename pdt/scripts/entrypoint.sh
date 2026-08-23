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

# Os seeds NÃO rodam por padrão na partida do container.
#
# Eles sobrescrevem aulas, questões e alternativas a partir dos arquivos em
# apps/*/seed_data/, apagando qualquer edição feita no admin. Como o container
# sobe a cada restart, OOM-kill e boot da EC2 (que é religada todo dia pelo
# agendamento de custo), deixá-los aqui significava apagar o conteúdo editado
# toda manhã, sem nenhum deploy.
#
# Para semear um banco novo (ou reaplicar os arquivos de propósito):
#   PDT_RUN_SEED=1 docker compose up      # na subida
#   docker compose exec web python manage.py seed_topics   # a qualquer momento
if [ "${PDT_RUN_SEED:-0}" = "1" ]; then
  echo ">> PDT_RUN_SEED=1: semeando conteúdo a partir dos arquivos de seed..."
  python manage.py seed_topics
  python manage.py seed_admission_test
  python manage.py seed_interviews
else
  echo ">> Seeds ignorados (defina PDT_RUN_SEED=1 para aplicá-los)."
fi

echo ">> Iniciando processo principal: $@"
exec "$@"
