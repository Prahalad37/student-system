#!/usr/bin/env bash
# Trigger a Render deploy non-interactively (no workspace/service prompts).
# Requires: RENDER_API_KEY, RENDER_SERVICE_ID (export or in .env).
#
# Usage:
#   export RENDER_API_KEY=rnd_xxx RENDER_SERVICE_ID=srv-xxx
#   ./scripts/render_deploy.sh
# Or: RENDER_API_KEY=... RENDER_SERVICE_ID=... ./scripts/render_deploy.sh
#
set -e
cd "$(dirname "$0")/.." || exit 1

if [ -z "${RENDER_API_KEY}" ]; then
  echo "Error: RENDER_API_KEY set karo (Render Dashboard → Account Settings → API Keys)"
  exit 1
fi
if [ -z "${RENDER_SERVICE_ID}" ]; then
  echo "Error: RENDER_SERVICE_ID set karo (school-erp service ID, e.g. srv-xxx from Dashboard or: render services -o json)"
  exit 1
fi

# Non-interactive: no prompts when API key + service ID are set
export CI=true
render deploys create "${RENDER_SERVICE_ID}" --wait --output json --confirm
