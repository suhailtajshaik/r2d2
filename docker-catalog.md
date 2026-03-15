# Docker Catalog — R2D2 VPS
# Source of truth for all containers. Guardian + agents reference this file.
# Last updated: 2026-03-15

---

## 🌐 Networks

```bash
# Create if missing (run once)
docker network create r2d2-proxy 2>/dev/null || true
```

| Network | Purpose |
|---------|---------|
| `r2d2-proxy` | Main proxy network — nginx + all sites + guardian |
| `prompt-studio` | Internal — prompt-studio + localai |

---

## 🟢 Always Running — Core

### r2d2-nginx
```yaml
# /home/r2d2/nginx/docker-compose.yml
services:
  r2d2-nginx:
    image: nginx:alpine
    container_name: r2d2-nginx
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks: [r2d2-proxy]
    restart: unless-stopped
```
```bash
cd /home/r2d2/nginx && docker compose up -d
```

### r2d2-guardian
```yaml
# /home/r2d2/guardian/docker-compose.yml
services:
  guardian:
    build: .
    container_name: r2d2-guardian
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock   # docker control
      - /home/r2d2/.openclaw:/root/.openclaw         # openclaw config
      - /home/r2d2/nginx:/home/r2d2/nginx            # nginx repair
      - /home/r2d2/guardian:/home/r2d2/guardian      # state + logs
      - /home/r2d2/brain:/home/r2d2/brain            # brain read/write
      - /home/r2d2/.config:/root/.config             # notion key
      - /home/r2d2/newspapers:/home/r2d2/newspapers  # newspaper archive
      - /home/r2d2/tools:/home/r2d2/tools            # websearch, logger
      - /home/r2d2/.claude:/root/.claude:ro          # 3PO auth
      - /home/r2d2/.ssh:/root/.ssh:ro                # git SSH key
    environment:
      - GUARDIAN_PHONE=+14699941765
      - GUARDIAN_CHANNEL=whatsapp
      - NOTION_API_KEY=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
      - TZ=America/New_York
    network_mode: host
```
```bash
cd /home/r2d2/guardian && docker compose up -d --build
```

---

## 🌐 Always Running — Sites

### portfolio
```yaml
services:
  portfolio:
    container_name: portfolio
    build: .
    networks: [r2d2-proxy]
    restart: unless-stopped
```
```bash
cd /home/r2d2/projects/portfolio && docker compose up -d --build
```

### lab
```yaml
services:
  lab:
    container_name: lab
    image: nginx:alpine
    volumes:
      - ./dist:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks: [r2d2-proxy]
    restart: unless-stopped
```
```bash
cd /home/r2d2/projects/lab-site && docker compose up -d
```

### prompt-studio
```yaml
services:
  prompt-studio:
    container_name: prompt-studio
    build: .
    networks: [r2d2-proxy]
    restart: unless-stopped
  localai:
    container_name: localai
    image: localai/localai:latest-aio-cpu
    networks: [r2d2-proxy]
    restart: unless-stopped
```
```bash
cd /home/r2d2/projects/prompt-studio && docker compose up -d --build
```

### news-site
```yaml
services:
  news-site:
    container_name: news-site
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /home/r2d2/newspapers:/usr/share/nginx/html/archive:ro
      - ./dist:/usr/share/nginx/html:ro
    networks: [r2d2-proxy]
    restart: unless-stopped
```
```bash
cd /home/r2d2/projects/news-site && docker compose up -d
```

---

## 🪖 On-Demand — Swarm Troopers

Swarm Troopers are ephemeral Claude Code instances. Spin up for a task, auto-terminate when done.
No Docker needed — they run as background processes on the host.

### Standard Trooper Launch
```bash
# Single trooper
cd /path/to/project
claude --permission-mode bypassPermissions --print 'YOUR TASK HERE

When done: openclaw system event --text "Trooper done: [summary]" --mode now' &
echo "Trooper PID: $!"
```

### Parallel Trooper Squad (multiple independent tasks)
```bash
# Launch squad
cd /home/r2d2/projects/myproject

claude --permission-mode bypassPermissions --print 'Task A — [description]. Push to development branch when done.' &
PID_A=$!

claude --permission-mode bypassPermissions --print 'Task B — [description]. Push to development branch when done.' &
PID_B=$!

claude --permission-mode bypassPermissions --print 'Task C — [description]. Push to development branch when done.' &
PID_C=$!

echo "Squad deployed: A=$PID_A B=$PID_B C=$PID_C"
```

### Trooper with full VPS access (for repairs)
```bash
claude --permission-mode bypassPermissions --print 'REPAIR TASK

Access:
- OpenClaw: /home/r2d2/.openclaw/
- Nginx: /home/r2d2/nginx/
- Projects: /home/r2d2/projects/
- Brain: /home/r2d2/brain/
- Tools: /home/r2d2/tools/
- Docker catalog: /home/r2d2/docker-catalog.md
- Notion logger: python3 /home/r2d2/tools/notion_logger.py
- Web search: python3 /home/r2d2/tools/websearch.py

YOUR TASK HERE

When done: openclaw system event --text "Done: [summary]" --mode now' &
```

### Trooper environment (what they inherit)
| Resource | Path | Access |
|----------|------|--------|
| Brain | `/home/r2d2/brain/` | Read/Write |
| Tools | `/home/r2d2/tools/` | Read/Execute |
| OpenClaw config | `/home/r2d2/.openclaw/` | Read |
| Git SSH key | `~/.ssh/` | Read |
| Claude auth | `~/.claude/` | Read |
| Notion API key | `~/.config/notion/api_key` | Read |
| Docker socket | `/var/run/docker.sock` | via host |

---

## 🤖 On-Demand — 3PO (Single Instance)

3PO is the senior coding partner. One at a time, focused on complex tasks.

```bash
# Standard 3PO launch
cd /home/r2d2/projects/TARGET_PROJECT
claude --permission-mode bypassPermissions --print 'DETAILED TASK

Git: push to development branch only, never master
Stack: [MERN/Python/Docker/React Native — as applicable]
Style: Stripe/Linear — minimal, clean, #6366F1 primary

TASK DETAILS HERE

When completely done:
- git add -A && git commit -m "..." && git push origin development
- openclaw system event --text "3PO done: [summary]" --mode now' &
```

---

## ⏸️ Stopped — Bring Up When Needed

### SellBridge Dev Stack
```bash
cd /home/r2d2/projects/Sellbridge && docker compose up -d
```

### GST Ledger Book
```bash
cd /home/r2d2/projects/gst-ledger-book && docker compose up -d
```

### RAG App
```bash
cd /home/r2d2/projects/rag-app && docker compose up -d
```

---

## 🧹 Cleanup Rules (Guardian auto-enforces)

| Trigger | Action | Command |
|---------|--------|---------|
| Reclaimable > 5GB | Auto-prune | `docker system prune -f` |
| Dangling images detected | Auto-prune | `docker image prune -f` |
| Stopped containers (non-catalog) | Auto-prune | `docker container prune -f` |
| Unused volumes | Monthly | `docker volume prune -f` |

**Protected — never prune:**
- r2d2-nginx, r2d2-guardian, portfolio, lab, prompt-studio, news-site, localai
- Any volume mounted to a running catalog container

---

## 📋 Quick Status Check

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker network ls | grep r2d2
docker system df
```
