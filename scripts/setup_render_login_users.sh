#!/usr/bin/env bash
# Run setup_login_users against Render DB from your machine (no Render Shell needed).
#
# 1. Render Dashboard → school-erp-db → Connect → External connection string copy karo
# 2. Run:
#      DATABASE_URL='postgresql://user:pass@host:5432/db' ./scripts/setup_render_login_users.sh
#    Or first deploy pe sirf demo users: add --run-if-empty
#      DATABASE_URL='...' ./scripts/setup_render_login_users.sh --run-if-empty
#
# Project root = parent of scripts/
set -e
cd "$(dirname "$0")/.." || exit 1

if [ -z "${DATABASE_URL}" ]; then
  echo "Error: DATABASE_URL set karo (Render Dashboard → school-erp-db → Connect → External URL)"
  exit 1
fi

python manage.py setup_login_users "$@"
