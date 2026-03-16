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

## 💼 ARIA (Multi-Tenant)
**Location on VPS:** `/home/r2d2/projects/aria/`
**Source backup:** `~/brain/agents/aria/src/`
**GitHub:** `suhailtajshaik/aria` (repo pending creation)
**Purpose:** Multi-tenant AI HR & Career Intelligence Agent — serves multiple companies AND candidates simultaneously with full data isolation.

**Deploy:**
```bash
mkdir -p /home/r2d2/projects/aria
cp -r ~/brain/agents/aria/src/* /home/r2d2/projects/aria/
cd /home/r2d2/projects/aria
docker compose up -d --build
```

**Run (multi-tenant CLI):**
```bash
# Candidates
python3 aria.py --new-candidate --name "John Doe" --email "john@example.com"
python3 aria.py --client cand_xxx --task intake
python3 aria.py --client cand_xxx --task resume_analysis
python3 aria.py --client cand_xxx --task tailor_resume --job "Staff Engineer at Stripe"
python3 aria.py --client cand_xxx --task linkedin
python3 aria.py --client cand_xxx --task brand
python3 aria.py --client cand_xxx --task portfolio

# Companies
python3 aria.py --new-company --name "Acme Corp" --industry "Tech"
python3 aria.py --client comp_xxx --task write_jd --role "Senior Engineer"
python3 aria.py --client comp_xxx --task screen_resumes --job job_xxx
python3 aria.py --client comp_xxx --task weekly_report

# Admin
python3 aria.py --list-clients
python3 aria.py --batch weekly_checkin
python3 aria.py --batch portfolio_sync
```

**Identity:**
- Name: ARIA (AI Recruitment & Career Intelligence Agent)
- Persona: Senior recruiter with 15 years at top-tier companies, now AI-powered
- Philosophy: Every candidate is a brand. Every resume is a marketing document.
- Architecture: Multi-tenant with UUID-based client IDs (cand_xxx / comp_xxx)

**Key features:**
- Multi-tenant: one instance serves companies + candidates with full data isolation
- Resume intelligence with ATS optimization
- LinkedIn profile rewrites (headline, about, experience)
- Portfolio site generator (single HTML, Tailwind CDN, dark/light toggle, JSON-LD, llms.txt)
- Personal brand architecture (UVP, positioning, content strategy)
- Company HR: job description writing, resume screening, weekly reports
- Batch ops: weekly check-ins for all candidates, portfolio sync
- ATS keyword analyzer with match scoring

---

## 🤖 3PO (Claude Code)
**Not a persistent agent — spawned on demand**
**Full docs:** `agents/3po/README.md`
**Purpose:** Heavy coding, debugging, building new features, infrastructure repair. R2D2's coding partner.

**Spawn pattern:**
```bash
cd /path/to/project && claude --permission-mode bypassPermissions --print 'task description'
```

**Install:** `npm install -g @anthropic-ai/claude-code`
**Used by:** R2D2 directly, and Guardian for complex repairs and permanent fixes

---

## Restore Order (after VPS wipe)
1. Restore R2D2: `bash ~/brain/restore.sh`
2. Deploy Guardian: `cd /home/r2d2/guardian && docker compose up -d --build`
3. Deploy Maxwell: already at `/home/r2d2/tools/editor-agent/` via restore
4. Deploy ARIA: `cp -r ~/brain/agents/aria/* /home/r2d2/projects/aria/`
5. Verify: `docker ps | grep guardian`
