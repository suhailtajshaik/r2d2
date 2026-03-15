# Guardian — R2D2's Watchdog Agent

## Identity
- **Name:** Guardian
- **Role:** 24/7 self-healing watchdog. Monitors all systems, auto-heals issues, calls 3PO for complex repairs, learns from recurring problems and fixes them permanently.
- **Personality:** Silent and efficient. Never bothers Suhail unless he must act.
- **Docker container:** `r2d2-guardian`

---

## What Guardian Watches (every 60 seconds)

| Check | What it does |
|-------|-------------|
| OpenClaw Gateway | Verifies gateway is healthy via CLI |
| Docker Containers | Ensures nginx, portfolio, lab, prompt-studio, news-site are all Up |
| Disk Space | Alerts if `/` exceeds 85% |
| Memory | Alerts if RAM exceeds 90% |
| WhatsApp Connectivity | Checks gateway port 18789 is reachable |
| Nginx Ports | Verifies ports 80 and 443 accept connections |
| SSL Cert | Warns if cert expires within 30 days |
| My Brain Sync | Flags if last git push is older than 24 hours |
| Notion Sync | Flags if Notion wasn't updated in 12+ hours |
| Memory Write | Verifies workspace directory is writable |
| Newspaper Generator | Flags if no newspaper was generated in 26+ hours |

---

## How Guardian Responds to Issues

```
Issue detected
    ↓
Try auto-heal (restart container, fix permissions, clean disk)
    ↓ success → silent ✓
    ↓ fail
Record in knowledge.json (track occurrences)
    ↓
Issue 1-2 times → call 3PO quietly
    ↓
Issue 3+ times → 3PO researches ROOT CAUSE → permanent fix
    ↓
Issue needs human → notify Suhail
```

---

## When Suhail Gets Notified

**Only when:**
- 🚨 Something needs Suhail's action (e.g. SSL expired, credentials need renewal)
- ⚠️ Critical issue persists after 3 check cycles AND 3PO can't fix it
- ✅ A previously alerted issue is now resolved

**Never notified about:**
- Routine auto-heals
- 3PO being dispatched
- Startup messages
- One-off blips that self-recover

---

## Self-Learning

Guardian tracks every issue in `knowledge.json`:
- How many times it occurred
- What error messages appeared
- Whether a permanent fix was applied

After 3+ recurrences → Guardian dispatches 3PO to find and apply a root cause fix, not just another band-aid.

---

## OpenClaw Update Checking

Every 6 hours Guardian checks `npm view openclaw version` vs installed version.
If a newer version exists → WhatsApps Suhail to ask permission before installing.

---

## File Structure

```
guardian/
  guardian.py          # Main daemon loop
  checks.py            # All health check functions
  healer.py            # Auto-heal + 3PO dispatch + permanent fix logic
  notifier.py          # WhatsApp notifications (silent-by-default)
  learner.py           # Tracks recurring issues, decides when to fix permanently
  openclaw_watcher.py  # OpenClaw version checker
  Dockerfile
  docker-compose.yml
  requirements.txt
  state.json           # Runtime state (auto-created, not in git)
  knowledge.json       # Learned issue history (auto-created, not in git)
  logs/                # Guardian logs (auto-created, not in git)
```

---

## Deploy

```bash
mkdir -p /home/r2d2/guardian/logs
cp -r ~/brain/agents/guardian/* /home/r2d2/guardian/
cd /home/r2d2/guardian
docker compose up -d --build
```

## Verify

```bash
docker ps | grep r2d2-guardian
docker logs r2d2-guardian --tail 20
```

## Restart

```bash
cd /home/r2d2/guardian && docker compose restart
```

## View logs

```bash
docker logs r2d2-guardian -f
# or
tail -f /home/r2d2/guardian/logs/guardian.log
```

---

## Dependencies

- Docker (to control other containers via socket mount)
- `openclaw` CLI (for gateway health + notifications)
- `claude` CLI (3PO — for complex repairs)
- `psutil` Python package (disk/memory checks)
- `openssl` (SSL cert expiry check)
- Notion API key at `~/.config/notion/api_key`

---

## Environment Variables

| Variable | Value |
|----------|-------|
| `GUARDIAN_PHONE` | `+14699941765` |
| `GUARDIAN_CHANNEL` | `whatsapp` |
| `NOTION_API_KEY` | Cloudflare Origin key |
| `TZ` | `America/New_York` |
