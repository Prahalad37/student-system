#!/bin/bash
# One-command deploy - pushes to GitHub & opens Render
set -e
cd "$(dirname "$0")"
echo "=== Git add & commit ==="
git add -A
git status
read -p "Commit message [Deploy ready]: " msg
msg=${msg:-Deploy ready}
git commit -m "$msg" || true
echo "=== Pushing to GitHub ==="
git push origin HEAD
echo ""
echo "✅ Pushed! Now deploy on Render:"
echo "   https://render.com/deploy?repo=https://github.com/Prahalad37/student-system"
echo ""
echo "Or: New → Blueprint → Connect repo → Select branch"
echo "Opening Render..."
open "https://render.com/deploy?repo=https://github.com/Prahalad37/student-system&branch=2026-01-23-ikne" 2>/dev/null || \
  xdg-open "https://render.com/deploy?repo=https://github.com/Prahalad37/student-system&branch=2026-01-23-ikne" 2>/dev/null || true
