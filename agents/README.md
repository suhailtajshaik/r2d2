# Agents — R2D2's Crew

These are autonomous agents that work alongside R2D2. All agents are preserved here so they can be fully restored after a VPS wipe.

---

## 🛡️ Guardian
**Location on VPS:** `/home/r2d2/guardian/`
**Docker container:** `r2d2-guardian`
**Purpose:** 24/7 watchdog — monitors all systems, auto-heals issues, calls 3PO for complex fixes, learns from recurring issues and fixes them permanently.

**Deploy:**
```bash
mkdir -p /home/r2d2/guardian
cp -r ~/brain/agents/guardian/* /home/r2d2/guardian/
cd /home/r2d2/guardian
docker compose up -d --build
```

**What it monitors:**
- OpenClaw gateway health
- Docker containers (nginx, portfolio, lab, prompt-studio, news-site)
- Disk space, memory
- Nginx ports 80/443
- SSL cert expiry
- My brain sync (git staleness)
- Notion sync (12h freshness)
- Workspace memory write access
- Newspaper generator health

**Notification rules:**
- Silent unless Suhail must act
- Alerts Suhail only when: action required, or critical issue persists 3+ cycles
- Notifies when previously alerted issue resolves

**Self-learning:**
- Tracks recurring issues in `knowledge.json`
- After 3+ occurrences → 3PO researches root cause → permanent fix applied
- OpenClaw update check every 6h → asks Suhail before installing

---

## ✏️ Maxwell
**Location on VPS:** `/home/r2d2/tools/editor-agent/`
**Purpose:** Senior news editor. Takes raw RSS data and produces clean, publication-ready journalism for The Headlines Today.

**Deploy:**
```bash
mkdir -p /home/r2d2/tools/editor-agent
cp -r ~/brain/agents/maxwell/* /home/r2d2/tools/editor-agent/
```

**Run:**
```bash
python3 /home/r2d2/tools/editor-agent/maxwell.py
```

**Identity:**
- Name: Maxwell
- Tone: Neutral, authoritative, Reuters/AP/Bloomberg style
- Output: Clean JSON articles — 150-200 words each, inverted pyramid, no URLs or junk
- Sections: World, AI & Tech, India, Hyderabad, Hot Topics, Business

**Used by:** `generate-newspaper.py` — called automatically every day at 5 AM EST

---

## 🤖 3PO (Claude Code)
**Not a persistent agent — spawned on demand**
**Purpose:** Heavy coding, debugging, building new features. R2D2's coding partner.

**Spawn pattern:**
```bash
cd /path/to/project && claude --permission-mode bypassPermissions --print 'task description'
```

**Used by:** R2D2 directly, and Guardian for complex repairs

---

## Restore Order (after VPS wipe)
1. Restore R2D2: `bash ~/brain/restore.sh`
2. Deploy Guardian: `cd /home/r2d2/guardian && docker compose up -d --build`
3. Deploy Maxwell: already at `/home/r2d2/tools/editor-agent/` via restore
4. Verify: `docker ps | grep guardian`
