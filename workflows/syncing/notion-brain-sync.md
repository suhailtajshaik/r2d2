# Workflow: Notion Brain Sync

**ID:** r2d2:notion-brain-sync  
**Category:** syncing  
**Enabled:** true  
**Cron:** `0 6 * * 5` (Fridays 6 AM EST)  
**Timezone:** America/New_York  

## Purpose
Weekly audit of brain infrastructure + Notion verification. Ensures:
- Skills folder matches Notion count
- Agents folder matches Notion count
- All cron jobs healthy + enabled
- Git history clean (no orphaned branches)
- VPS resources healthy (disk, memory)

**Impact:** Detects infrastructure drift early; prevents silent failures

## Schedule
- **Frequency:** Fridays at 6 AM EST (weekly)
- **Timezone:** America/New_York (EST/EDT)
- **Next Run:** Next Friday, 6 AM (~4d 21h)
- **Last Run:** 2 days ago ✅
- **Status:** ✅ Active

## Execution
- **Agent:** R2D2 (isolated session)
- **Timeout:** 120 seconds
- **Script:** `bash /home/r2d2/tools/notion-sync-brain.sh`

## Verification Steps
1. **Skills Count:** `ls -1 brain/skills/ | wc -l` vs Notion Skills DB
2. **Agents Count:** `ls -1 brain/agents/ | wc -l` vs Notion Agents DB
3. **Cron Jobs:** Via cron API — all enabled? Any errors?
4. **Git Status:**
   - No uncommitted changes (should be auto-committed)
   - No orphaned branches (cleanup)
   - Recent commits (last commit <24h)
5. **VPS Health:**
   - Disk: `df -h /` (<80% used)
   - Memory: `free -h` (<80% used)
   - Containers: All running + healthy

## Monitoring
- **Health Check:** All 5 verifications pass
- **Alerts:**
  - Skills count mismatch → alert (manual review needed)
  - Agents count mismatch → alert (manual review needed)
  - Cron errors → alert (check logs)
  - Disk >80% → alert (cleanup needed)
  - Memory >80% → alert (restart containers?)
  - Git uncommitted → warning (not critical)

- **Alert Threshold:** Any mismatch = notify Suhail
- **Remediation:** Manual review — could indicate stale backup or recent deployment

## Output
- **Destination:** WhatsApp (bestEffort: true)
- **Message Format:** "Notion brain sync complete" if all OK, or list of issues if any found

## Files
- **Script:** `/home/r2d2/tools/notion-sync-brain.sh`
- **Notion API Key:** `~/.config/notion/api_key`
- **Page IDs:**
  - VPS State: `323c2d43-b275-817f-a619-ebfb96d72aa2`
  - Agents: `324c2d43-b275-8179-aeb3-c22edc04ee68`
  - Operating Rules: `323c2d43-b275-8141-90db-f6c3a8cc288f`

## Integration
- **Part of:** Brain integrity + Notion sync system
- **Depends on:** Notion API + brain/ directory + cron backend
- **Triggered by:** Cron Fridays 6 AM
- **Delivers to:** WhatsApp (errors only)
- **Related to:** Monthly brain tag (1st of month)

## Maintenance
- **Last updated:** 2026-03-20
- **Last run status:** ✅ OK (Notion in sync)
- **Skills count:** 36 (as of March 15)
- **Agents count:** 3 (Guardian, Maxwell, 3PO)
- **Next audit:** Next Friday 6 AM

---

**Cron Job ID:** `b5085885-1ec2-4270-9770-19ac66c4f31a`  
**Created:** 2026-03-19  
**Type:** Weekly infrastructure audit
