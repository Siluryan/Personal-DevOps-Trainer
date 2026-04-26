#!/usr/bin/env bash
# Traz o commit do GitHub (incl. clones rasos) e faz reset a essa ref.
# Uso: git-fetch-reset-deploy-ref.sh <sha40> [dir=/opt/pdt/app]
# Chamado pelo SSM a partir do deploy no GitHub Actions.
set -euo pipefail
SHA="${1:?commit sha obrigatorio}"
REPO_DIR="${2:-/opt/pdt/app}"
cd "$REPO_DIR"

set +e
git fetch --unshallow 2>/dev/null
git fetch origin
git fetch origin "refs/heads/main:refs/remotes/origin/main" 2>/dev/null

if ! git rev-parse -q --verify "$SHA^{commit}" >/dev/null 2>&1; then
  for depth in 200 2000 20000 100000; do
    git rev-parse -q --verify "$SHA^{commit}" >/dev/null 2>&1 && break
    git fetch --depth="$depth" origin 2>/dev/null || true
  done
fi

if ! git rev-parse -q --verify "$SHA^{commit}" >/dev/null 2>&1; then
  git fetch --unshallow 2>/dev/null
  git fetch origin
fi

set -e
if ! git rev-parse -q --verify "$SHA^{commit}" >/dev/null 2>&1; then
  echo "ERROR: nao encontro o object $SHA (clone raso/ shallow?). Tente: git -C $REPO_DIR fetch --unshallow && git -C $REPO_DIR fetch origin" >&2
  exit 128
fi

git reset --hard "$SHA"
exit 0
