# R2D2 — Restore Guide

If you're reading this, OpenClaw was reinstalled fresh. This is how to get back to full operational state.

---

## Step 1 — Tell R2D2 to restore

Say: **"Restore yourself from git: git@github.com:suhailtajshaik/r2d2.git"**

R2D2 will clone this repo and follow the steps below automatically.

---

## Step 2 — Clone the brain repo

```bash
cd /home/r2d2
git clone git@github.com:suhailtajshaik/r2d2.git brain
```

---

## Step 3 — Restore workspace files

```bash
cp /home/r2d2/brain/workspace/MEMORY.md   /home/r2d2/.openclaw/workspace/
cp /home/r2d2/brain/workspace/SOUL.md     /home/r2d2/.openclaw/workspace/
cp /home/r2d2/brain/workspace/USER.md     /home/r2d2/.openclaw/workspace/
cp /home/r2d2/brain/workspace/AGENTS.md   /home/r2d2/.openclaw/workspace/
cp /home/r2d2/brain/workspace/TOOLS.md    /home/r2d2/.openclaw/workspace/
cp /home/r2d2/brain/workspace/IDENTITY.md /home/r2d2/.openclaw/workspace/
cp /home/r2d2/brain/workspace/HEARTBEAT.md /home/r2d2/.openclaw/workspace/

# Restore daily memory logs
mkdir -p /home/r2d2/.openclaw/workspace/memory
cp /home/r2d2/brain/memory/*.md /home/r2d2/.openclaw/workspace/memory/ 2>/dev/null
cp /home/r2d2/brain/memory/*.json /home/r2d2/.openclaw/workspace/memory/ 2>/dev/null
```

---

## Step 4 — Restore global git config

```bash
cp /home/r2d2/brain/vps/gitconfig-r2d2 ~/.gitconfig
```

Or set manually:
```bash
git config --global user.email "suhailtajshaik@gmail.com"
git config --global user.name "R2D2"
git config --global init.defaultBranch master
```

---

## Step 5 — Restore Notion API key config

```bash
mkdir -p ~/.config/notion
# Set NOTION_API_KEY env var or:
echo "$NOTION_API_KEY" > ~/.config/notion/api_key
```

---

## Step 6 — Verify SSH key for GitHub

```bash
ssh -T git@github.com
# Should say: Hi suhailtajshaik!
```

If not: generate new key, add to GitHub settings.
```bash
ssh-keygen -t ed25519 -C "suhailtajshaik@gmail.com" -f ~/.ssh/github_r2d2 -N ""
cat ~/.ssh/github_r2d2.pub
# Add to: github.com/settings/keys
```

---

## Step 7 — Check VPS containers

```bash
docker ps -a
# Restart what's needed:
cd /home/r2d2/nginx && docker compose up -d
cd /home/r2d2/projects/portfolio && docker compose up -d
cd /home/r2d2/projects/lab-site && docker compose up -d
cd /home/r2d2/projects/prompt-studio && docker compose up -d
```

---

## What R2D2 Knows After Restore

- **Who Suhail is** — USER.md
- **Who R2D2 is** — SOUL.md + IDENTITY.md
- **All operating rules** — MEMORY.md + memory/operating-rules.md
- **All project statuses** — vps/github-remotes.md
- **VPS architecture** — vps/state.md
- **Session history** — memory/YYYY-MM-DD.md files
- **Notion space** — notion.so/suhailtaj/R2D2...

---

## Key References

| Thing | Value |
|-------|-------|
| Brain repo | git@github.com:suhailtajshaik/r2d2.git |
| Notion | https://www.notion.so/suhailtaj/R2D2-323c2d43b27580438ab2df3def34f932 |
| Portfolio | https://suhailtaj.cloud |
| Lab | https://lab.suhailtaj.cloud |
| Prompt Studio | https://lab.suhailtaj.cloud/prompt-studio |
| Suhail's email | suhailtajshaik@gmail.com |
| GitHub | suhailtajshaik |
