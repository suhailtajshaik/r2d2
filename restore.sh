#!/usr/bin/env bash
set -euo pipefail

# R2D2 Full Restore Script
# Run this after a fresh OpenClaw install to get back to full operational state.
# Usage: bash /home/r2d2/brain/restore.sh

BRAIN_DIR="/home/r2d2/brain"
OPENCLAW_DIR="/home/r2d2/.openclaw/workspace"
PROJECTS_DIR="/home/r2d2/projects"
NGINX_DIR="/home/r2d2/nginx"

echo "=========================================="
echo "  R2D2 RESTORE — Full System Recovery"
echo "=========================================="

# --- Step 1: Verify brain repo exists ---
if [ ! -d "$BRAIN_DIR" ]; then
  echo "[1/7] Cloning brain repo..."
  cd /home/r2d2
  git clone git@github.com:suhailtajshaik/r2d2.git brain
else
  echo "[1/7] Brain repo already exists — pulling latest..."
  cd "$BRAIN_DIR" && git pull origin master
fi

# --- Step 2: Restore custom skills ---
echo "[2/7] Restoring 26 custom skills..."
mkdir -p "$OPENCLAW_DIR/skills"
cp -r "$BRAIN_DIR/skills/"* "$OPENCLAW_DIR/skills/" 2>/dev/null || echo "  ⚠ No skills found to copy"
echo "  ✓ Skills restored to $OPENCLAW_DIR/skills/"

# --- Step 3: Restore workspace files ---
echo "[3/7] Restoring workspace files..."
mkdir -p "$OPENCLAW_DIR"
for file in MEMORY.md SOUL.md USER.md AGENTS.md TOOLS.md IDENTITY.md HEARTBEAT.md; do
  if [ -f "$BRAIN_DIR/workspace/$file" ]; then
    cp "$BRAIN_DIR/workspace/$file" "$OPENCLAW_DIR/$file"
    echo "  ✓ $file"
  fi
done

# Restore memory logs
mkdir -p "$OPENCLAW_DIR/memory"
cp "$BRAIN_DIR/memory/"*.md "$OPENCLAW_DIR/memory/" 2>/dev/null || true
cp "$BRAIN_DIR/memory/"*.json "$OPENCLAW_DIR/memory/" 2>/dev/null || true
echo "  ✓ Memory logs restored"

# --- Step 4: Restore git config ---
echo "[4/7] Restoring git config..."
if [ -f "$BRAIN_DIR/vps/gitconfig-r2d2" ]; then
  cp "$BRAIN_DIR/vps/gitconfig-r2d2" ~/.gitconfig
  echo "  ✓ Git config restored"
else
  git config --global user.email "suhailtajshaik@gmail.com"
  git config --global user.name "R2D2"
  git config --global init.defaultBranch master
  echo "  ✓ Git config set manually"
fi

# --- Step 5: Verify SSH ---
echo "[5/7] Checking GitHub SSH..."
if ssh -T git@github.com 2>&1 | grep -q "suhailtajshaik"; then
  echo "  ✓ SSH key works"
else
  echo "  ⚠ SSH key not recognized — generate one:"
  echo "    ssh-keygen -t ed25519 -C 'suhailtajshaik@gmail.com' -f ~/.ssh/github_r2d2 -N ''"
  echo "    Add ~/.ssh/github_r2d2.pub to github.com/settings/keys"
fi

# --- Step 6: Restore Nginx config ---
echo "[6/7] Restoring Nginx configs..."
if [ -d "$BRAIN_DIR/vps/nginx-conf" ]; then
  mkdir -p "$NGINX_DIR"
  cp "$BRAIN_DIR/vps/nginx-conf/nginx.conf" "$NGINX_DIR/nginx.conf" 2>/dev/null || true
  cp -r "$BRAIN_DIR/vps/nginx-conf/conf.d" "$NGINX_DIR/conf.d" 2>/dev/null || true
  cp "$BRAIN_DIR/vps/nginx-conf/docker-compose.yml" "$NGINX_DIR/docker-compose.yml" 2>/dev/null || true
  echo "  ✓ Nginx configs restored to $NGINX_DIR/"
else
  echo "  ⚠ No nginx configs found in brain repo"
fi

# --- Step 7: Start containers ---
echo "[7/7] Starting Docker containers..."
if command -v docker &>/dev/null; then
  # Start nginx first (reverse proxy for everything)
  if [ -f "$NGINX_DIR/docker-compose.yml" ]; then
    cd "$NGINX_DIR" && docker compose up -d 2>/dev/null && echo "  ✓ r2d2-nginx started" || echo "  ⚠ nginx failed to start"
  fi

  # Start project containers
  for project in portfolio lab-site prompt-studio; do
    if [ -f "$PROJECTS_DIR/$project/docker-compose.yml" ]; then
      cd "$PROJECTS_DIR/$project" && docker compose up -d 2>/dev/null && echo "  ✓ $project started" || echo "  ⚠ $project failed"
    fi
  done
else
  echo "  ⚠ Docker not installed — install it first"
fi

echo ""
echo "=========================================="
echo "  RESTORE COMPLETE"
echo "=========================================="
echo ""
echo "Still needed (manual):"
echo "  - Set NOTION_API_KEY if not already in environment"
echo "  - Verify: docker ps -a"
echo "  - Verify: curl -s https://suhailtaj.cloud | head -5"
echo ""
