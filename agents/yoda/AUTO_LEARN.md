# Yoda Auto-Learning System

## Purpose
Automatically feed lessons, documentation, and knowledge from brain/ and projects/ into Yoda's knowledge base.

## Trigger Points
Yoda learns from:
1. **New lessons** → `brain/lessons/*.md` → feed to Yoda immediately
2. **New PDFs** → `brain/resources/*.pdf` → parse and feed
3. **Code reviews** → `brain/docs/*.md` → feed architecture/patterns
4. **Session insights** → marked with `[YODA_LEARN]` in MEMORY.md → auto-extract
5. **Project changes** → committed code → auto-analyze and feed improvements

## Implementation
Create a cron job that:
1. Scans `brain/lessons/` for new `.md` files
2. Feeds each to Yoda via `python agent.py learn --file <path>`
3. Logs result to `yoda/knowledge/auto_learn_log.md`
4. Commits updated knowledge base

## Auto-Learn Command
```bash
cd /home/r2d2/projects/yoda
python agent.py learn --file /home/r2d2/brain/lessons/api-architecture-mistake.md
```

## Cron Job (proposed)
- **Frequency:** Every 6 hours
- **Time:** 2 AM, 8 AM, 2 PM, 8 PM EST
- **Script:** `yoda_auto_learn.sh`
- **Notification:** Silent (logs only)

## Files to Auto-Learn From
- `brain/lessons/*.md` (new mistakes & lessons)
- `brain/docs/*.md` (architecture, patterns, standards)
- `MEMORY.md` sections marked `[YODA_LEARN]`
- `code-review-checklist.md` (standards to enforce)
- Any `*.pdf` in `brain/resources/`

## Status
- ⚠️ Manual feed working (tested March 17)
- ⏳ Cron automation pending
- 📋 Script template ready for creation

## Next Steps
1. Create `yoda_auto_learn.sh` script
2. Test with existing brain/lessons/
3. Schedule cron job
4. Monitor knowledge base growth
