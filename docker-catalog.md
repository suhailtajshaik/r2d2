# Docker Catalog — R2D2 VPS

All containers, images, and networks managed by R2D2.
Guardian references this to know what should be running and what's safe to prune.

---

## 🟢 Core Infrastructure (always running)

| Container | Image | Purpose | Compose Location |
|-----------|-------|---------|-----------------|
| `r2d2-nginx` | `nginx:alpine` | Reverse proxy — routes all domains | `/home/r2d2/nginx/` |
| `r2d2-guardian` | `guardian-guardian` | Watchdog agent — monitors + heals | `/home/r2d2/guardian/` |

## 🌐 Sites (always running)

| Container | Image | URL | Compose Location |
|-----------|-------|-----|-----------------|
| `portfolio` | `portfolio-portfolio` | suhailtaj.cloud | `/home/r2d2/projects/portfolio/` |
| `lab` | `nginx:alpine` | lab.suhailtaj.cloud | `/home/r2d2/projects/lab-site/` |
| `prompt-studio` | `prompt-studio-prompt-studio` | lab.suhailtaj.cloud/prompt-studio/ | `/home/r2d2/projects/prompt-studio/` |
| `news-site` | `nginx:alpine` | news.suhailtaj.cloud | `/home/r2d2/projects/news-site/` |

## 🔧 Services (always running)

| Container | Image | Purpose | Compose Location |
|-----------|-------|---------|-----------------|
| `localai` | `localai/localai:latest-aio-cpu` | Local LLM inference | `/home/r2d2/projects/prompt-studio/` |

## ⏸️ Stopped (bring up when needed)

| Container | Purpose | Compose Location |
|-----------|---------|-----------------|
| `sellbridge-*` | SellBridge dev stack | `/home/r2d2/projects/Sellbridge/` |
| `gst-ledger` | GST Ledger Book | `/home/r2d2/projects/gst-ledger-book/` |
| `rag-app-*` | RAG App stack | `/home/r2d2/projects/rag-app/` |

---

## 🌐 Docker Networks

| Network | Used By |
|---------|---------|
| `r2d2-proxy` | nginx, portfolio, lab, prompt-studio, news-site, guardian |
| `prompt-studio` | prompt-studio, localai |

---

## 🧹 Cleanup Rules (Guardian auto-enforces)

| Rule | Threshold | Action |
|------|-----------|--------|
| Reclaimable disk > 5GB | Weekly check | `docker system prune -f` (images + containers + volumes) |
| Dangling images | On detection | `docker image prune -f` |
| Stopped containers > 7 days | Weekly | `docker container prune -f` |
| Unused volumes | Monthly | `docker volume prune -f` |

**NEVER prune:**
- Any container listed in Core Infrastructure or Sites above
- Any named volume with active data (check before pruning)

---

## 🔄 Rebuild Commands

```bash
# Nginx
cd /home/r2d2/nginx && docker compose up -d

# Portfolio
cd /home/r2d2/projects/portfolio && docker compose up -d --build

# Lab
cd /home/r2d2/projects/lab-site && docker compose up -d

# Prompt Studio
cd /home/r2d2/projects/prompt-studio && docker compose up -d --build

# News Site
cd /home/r2d2/projects/news-site && docker compose up -d

# Guardian
cd /home/r2d2/guardian && docker compose up -d --build
```

---

## 🪖 Swarm Troopers (temporary containers)

Swarm Troopers are temporary Claude Code instances spun up in parallel for independent tasks.
They are NOT in this catalog — they are ephemeral, spawn and terminate on task completion.

Pattern: `claude --permission-mode bypassPermissions --print 'task' &`
Multiple can run simultaneously for parallel work.
3PO coordinates them. R2D2 orchestrates 3PO.
