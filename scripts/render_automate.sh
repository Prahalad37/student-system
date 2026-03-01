#!/usr/bin/env bash
# Render CLI automation: deploy, status, logs.
# Usage:
#   ./scripts/render_automate.sh deploy     # Trigger deploy (wait for completion)
#   ./scripts/render_automate.sh status     # Show latest deploy status
#   ./scripts/render_automate.sh deploy-now  # Same as deploy (alias)
#
# Requires one of:
#   A) RENDER_API_KEY + RENDER_SERVICE_ID (CI / non-interactive)
#   B) render login + render workspace set (interactive)
#
# Service ID: srv-d63h5o7gi27c739g79f0 (school-erp)
#
set -e
cd "$(dirname "$0")/.." || exit 1

SERVICE_ID="${RENDER_SERVICE_ID:-srv-d63h5o7gi27c739g79f0}"

cmd="${1:-deploy}"
case "$cmd" in
  deploy|deploy-now)
    echo ">>> Deploying school-erp (service: $SERVICE_ID)..."
    export CI=true
    if [ -n "${RENDER_API_KEY}" ]; then
      render deploys create "$SERVICE_ID" --wait --output json --confirm
    else
      render deploys create "$SERVICE_ID" --wait --confirm
    fi
    echo ">>> Deploy complete. Check: https://school-erp-51hd.onrender.com/health/"
    ;;
  status)
    echo ">>> Latest deploys for school-erp:"
    render deploys list "$SERVICE_ID" -o json 2>/dev/null | head -50 || render deploys list "$SERVICE_ID"
    ;;
  *)
    echo "Usage: $0 {deploy|deploy-now|status}"
    echo "  deploy     - Trigger deploy and wait"
    echo "  deploy-now  - Same as deploy"
    echo "  status     - Show latest deploy status"
    exit 1
    ;;
esac
