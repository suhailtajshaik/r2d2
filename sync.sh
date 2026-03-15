#!/usr/bin/env bash
set -euo pipefail

# R2D2 Sync Script — workspace files → brain repo → GitHub
# Idempotent: safe to run anytime, only commits if there are changes.
# Usage: bash /home/r2d2/brain/sync.sh [commit message]

BRAIN_DIR="/home/r2d2/brain"
OPENCLAW_DIR="/home/r2d2/.openclaw/workspace"
NGINX_DIR="/home/r2d2/nginx"
COMMIT_MSG="${1:-sync: workspace → brain repo (auto)}"

echo "=== R2D2 SYNC ==="

# --- Sync workspace files → brain repo ---
echo "[1/4] Syncing workspace files..."
mkdir -p "$BRAIN_DIR/workspace"
for file in MEMORY.md SOUL.md USER.md AGENTS.md TOOLS.md IDENTITY.md HEARTBEAT.md; do
  if [ -f "$OPENCLAW_DIR/$file" ]; then
    cp "$OPENCLAW_DIR/$file" "$BRAIN_DIR/workspace/$file"
  fi
done
echo "  ✓ Workspace files synced"

# --- Sync memory logs ---
echo "[2/4] Syncing memory logs..."
mkdir -p "$BRAIN_DIR/memory"
if [ -d "$OPENCLAW_DIR/memory" ]; then
  cp "$OPENCLAW_DIR/memory/"*.md "$BRAIN_DIR/memory/" 2>/dev/null || true
  cp "$OPENCLAW_DIR/memory/"*.json "$BRAIN_DIR/memory/" 2>/dev/null || true
  echo "  ✓ Memory logs synced"
else
  echo "  ⚠ No memory directory found in workspace"
fi

# --- Sync skills ---
echo "[3/4] Syncing skills..."
if [ -d "$OPENCLAW_DIR/skills" ]; then
  mkdir -p "$BRAIN_DIR/skills"
  rsync -a --delete "$OPENCLAW_DIR/skills/" "$BRAIN_DIR/skills/" 2>/dev/null || \
    cp -r "$OPENCLAW_DIR/skills/"* "$BRAIN_DIR/skills/" 2>/dev/null || true
  echo "  ✓ Skills synced"
else
  echo "  ⚠ No skills directory found"
fi

# --- Sync nginx configs ---
if [ -d "$NGINX_DIR" ]; then
  mkdir -p "$BRAIN_DIR/vps/nginx-conf/conf.d/common"
  cp "$NGINX_DIR/nginx.conf" "$BRAIN_DIR/vps/nginx-conf/nginx.conf" 2>/dev/null || true
  cp -r "$NGINX_DIR/conf.d/"* "$BRAIN_DIR/vps/nginx-conf/conf.d/" 2>/dev/null || true
  cp "$NGINX_DIR/docker-compose.yml" "$BRAIN_DIR/vps/nginx-conf/docker-compose.yml" 2>/dev/null || true
  echo "  ✓ Nginx configs synced"
fi

# --- Git commit + push (only if changes exist) ---
echo "[4/4] Committing & pushing..."
cd "$BRAIN_DIR"

git add -A

if git diff --cached --quiet; then
  echo "  ✓ No changes to commit — already in sync"
else
  git commit -m "$COMMIT_MSG"
  git push origin master
  echo "  ✓ Committed and pushed to GitHub"
fi

echo ""
echo "=== SYNC COMPLETE ==="
