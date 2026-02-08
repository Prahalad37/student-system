#!/usr/bin/env bash
# Full workflow: trigger Render deploy, then (if DATABASE_URL set) reset demo login users.
# Requires: RENDER_API_KEY, RENDER_SERVICE_ID. Optional: DATABASE_URL for step 2.
#
# Usage:
#   export RENDER_API_KEY=... RENDER_SERVICE_ID=...
#   export DATABASE_URL=...   # optional, for resetting login users after deploy
#   ./scripts/render_workflow.sh
#
set -e
cd "$(dirname "$0")/.." || exit 1

# Step 1: Deploy (always)
./scripts/render_deploy.sh

# Step 2: Reset demo users if DATABASE_URL is set
if [ -n "${DATABASE_URL}" ]; then
  echo "Resetting demo login users (DATABASE_URL set)..."
  ./scripts/setup_render_login_users.sh
else
  echo "DATABASE_URL not set; skipping login users reset. Set it to run setup_login_users after deploy."
fi
