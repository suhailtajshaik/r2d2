# Yoda Agent - Notion Page Data

**Copy this to Notion immediately**

---

## Page Title
**Yoda**

## Properties

### Type
**Python Agent + Scheduler**

### Status
**Running ✅ (4x daily: 2 AM, 8 AM, 2 PM, 8 PM EST)**

### Role
**Autonomous knowledge expansion and continuous learning**

### Description

Yoda is an autonomous agent that monitors knowledge gaps, identifies trending topics, researches new information, and automatically updates Suhail's knowledge base with synthesized guides.

**Features:**
- Knowledge Gap Detection — Identifies missing guides
- Trend Monitoring — Tracks emerging topics
- Automatic Research — Web search and synthesis
- Self-Improvement — Reviews and updates past guides
- Weekly Digest — "What We Learned" summary
- MEMORY.md Integration — Updates long-term memory

### Location
`/home/r2d2/brain/agents/yoda/`

### Schedule
- 2:00 AM EST — Deep learning & research
- 8:00 AM EST — Morning briefing & gap detection
- 2:00 PM EST — Trending topics check
- 8:00 PM EST — End-of-day synthesis

### Key Files
- `yoda_learning_agent.py` — Main learning loop
- `yoda_scheduler.sh` — Cron scheduler (executable)
- `learning_state.json` — Agent state tracking
- `/home/r2d2/projects/yoda/knowledge/` — Knowledge base

### Logs
- Daily: `/home/r2d2/.openclaw/workspace/memory/yoda_learning_YYYY-MM-DD.log`
- Weekly digest: `/home/r2d2/brain/agents/yoda/digest_YYYY-MM-DD.md`

### Dependencies
- Python 3.8+
- requests library
- Perplexity API (optional, for enhanced research)
- Claude API (optional, for intelligent synthesis)

### How to Run

**Manual:**
```bash
cd /home/r2d2/brain/agents/yoda
python3 yoda_learning_agent.py
```

**Check state:**
```bash
cat learning_state.json
```

**View logs:**
```bash
tail -f /home/r2d2/.openclaw/workspace/memory/yoda_learning_$(date +%Y-%m-%d).log
```

### Integration Points
1. **Knowledge Base** → `/home/r2d2/projects/yoda/knowledge/`
2. **MEMORY.md Updates** → `/home/r2d2/.openclaw/workspace/MEMORY.md`
3. **Trending Topics** → Via Perplexity web search
4. **Weekly Digest** → Generated Mondays

### Created
2026-03-20

### Last Updated
2026-03-21

### Related Agents
- **Guardian** — Infrastructure watchdog
- **Maxwell** — News editor
- **3PO** — Coding partner
- **Voice Agent** — Ask about learnings via voice
- **Video Agent** — Generate educational videos

---

## Quick Copy Template

```
Agent Name: Yoda
Type: Python Agent + Scheduler
Status: Running ✅ (4x daily)
Role: Autonomous knowledge expansion and learning
Location: /home/r2d2/brain/agents/yoda/
Schedule: 2 AM, 8 AM, 2 PM, 8 PM EST
Knowledge Base: /home/r2d2/projects/yoda/knowledge/
Logs: /home/r2d2/.openclaw/workspace/memory/yoda_learning_*.log
```
