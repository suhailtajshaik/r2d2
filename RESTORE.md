# R2D2 — Restore Guide

If you're reading this, OpenClaw was reinstalled fresh. This is how to get back to full operational state.

---

## Quick Restore (One Command)

After cloning the brain repo, run the automated restore script:

```bash
cd /home/r2d2
git clone git@github.com:suhailtajshaik/r2d2.git brain
bash /home/r2d2/brain/restore.sh
```

That's it. The script handles steps 2-7 below automatically. Read on only if you need to do it manually or debug issues.

---

## Manual Steps (if restore.sh fails)

### Step 1 — Clone the brain repo

```bash
cd /home/r2d2
git clone git@github.com:suhailtajshaik/r2d2.git brain
```

### Step 2 — Restore custom skills

```bash
cp -r /home/r2d2/brain/skills/* /home/r2d2/.openclaw/workspace/skills/
```

26 custom skills: `senior-*` (13 roles), `ceo-advisor`, `cto-advisor`, `server-health`, `send-document`, `firecrawl-search`, `ui-ux-pro-max`, `code-reviewer`, `tdd-guide`, `tech-stack-evaluator`, `last30days`, `screenshot`, `prd`, `gsd`

### Step 3 — Restore workspace files

```bash
cp /home/r2d2/brain/workspace/*.md /home/r2d2/.openclaw/workspace/
mkdir -p /home/r2d2/.openclaw/workspace/memory
cp /home/r2d2/brain/memory/*.md /home/r2d2/.openclaw/workspace/memory/ 2>/dev/null
cp /home/r2d2/brain/memory/*.json /home/r2d2/.openclaw/workspace/memory/ 2>/dev/null
```

### Step 4 — Restore git config

```bash
cp /home/r2d2/brain/vps/gitconfig-r2d2 ~/.gitconfig
```

### Step 5 — Restore Notion API key

```bash
# Set NOTION_API_KEY in your environment or:
mkdir -p ~/.config/notion
echo "$NOTION_API_KEY" > ~/.config/notion/api_key
```

### Step 6 — Verify SSH key for GitHub

```bash
ssh -T git@github.com
# Should say: Hi suhailtajshaik!
```

If not:
```bash
ssh-keygen -t ed25519 -C "suhailtajshaik@gmail.com" -f ~/.ssh/github_r2d2 -N ""
cat ~/.ssh/github_r2d2.pub
# Add to: github.com/settings/keys
```

### Step 7 — Restore Nginx + Start containers

```bash
# Nginx configs are restored by restore.sh, but manually:
cp -r /home/r2d2/brain/vps/nginx-conf/* /home/r2d2/nginx/

# Start containers:
cd /home/r2d2/nginx && docker compose up -d
cd /home/r2d2/projects/portfolio && docker compose up -d
cd /home/r2d2/projects/lab-site && docker compose up -d
cd /home/r2d2/projects/prompt-studio && docker compose up -d
```

---

## Post-Restore Verification Checklist

```bash
# All of these should pass:
docker ps                                    # nginx, portfolio, lab, prompt-studio running
curl -s https://suhailtaj.cloud | head -5    # portfolio loads
curl -s https://lab.suhailtaj.cloud | head -5 # lab loads
ssh -T git@github.com                        # SSH works
git -C /home/r2d2/brain log --oneline -3     # brain repo has history
```

---

## What R2D2 Knows After Restore

| File | Contains |
|------|----------|
| `workspace/USER.md` | Who Suhail is |
| `workspace/SOUL.md` + `IDENTITY.md` | Who R2D2 is |
| `workspace/MEMORY.md` | Long-term memory + operating context |
| `memory/operating-rules.md` | How we work together |
| `vps/github-remotes.md` | All projects + GitHub URLs + versions |
| `vps/state.md` | VPS architecture + running containers |
| `memory/YYYY-MM-DD.md` | Session history |
| `research/HOW_TO_LEARN.md` | Self-improvement patterns |

---

## Key References

| Thing | Value |
|-------|-------|
| Brain repo | `git@github.com:suhailtajshaik/r2d2.git` |
| Notion | https://www.notion.so/suhailtaj/R2D2-323c2d43b27580438ab2df3def34f932 |
| Portfolio | https://suhailtaj.cloud |
| Lab | https://lab.suhailtaj.cloud |
| Prompt Studio | https://lab.suhailtaj.cloud/prompt-studio |
| Suhail's email | suhailtajshaik@gmail.com |
| GitHub | suhailtajshaik |

---

## Ongoing Sync

After restore, use `sync.sh` to keep the brain repo up to date:

```bash
bash /home/r2d2/brain/sync.sh
# or with a custom commit message:
bash /home/r2d2/brain/sync.sh "sync: post-session update"
```
