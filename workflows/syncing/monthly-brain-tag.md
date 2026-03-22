# Workflow: Monthly Brain Tag

**ID:** r2d2:monthly-brain-tag  
**Category:** syncing  
**Enabled:** true  
**Cron:** `0 6 1 * *` (1st of month at 6 AM EST)  
**Timezone:** America/New_York  

## Purpose
Create an immutable monthly snapshot of the entire brain repository. Tags serve as recovery points if something breaks badly. Each tag includes:
- Month snapshot (YYYY-MM format)
- Skills count at snapshot time
- Agents count at snapshot time
- Timestamp + summary

**Impact:** Gives us a reliable rollback point if infrastructure needs recovery

## Schedule
- **Frequency:** First day of each month at 6 AM EST
- **Timezone:** America/New_York (EST/EDT)
- **Next Run:** April 1st, 6 AM (~9 days)
- **Last Run:** Never (Feb 1st was before ClawFlows launched)
- **Status:** ✅ Ready

## Execution
- **Agent:** R2D2 (isolated session)
- **Timeout:** 300 seconds
- **Script:** Commands:
  ```bash
  cd /home/r2d2/brain
  
  # Sync first (ensure brain is fully up-to-date)
  bash sync.sh
  
  # Create annotated tag with metadata
  MONTH=$(date +%Y-%m)
  TAG="brain-${MONTH}"
  SKILL_COUNT=$(ls skills/ | wc -l)
  AGENT_COUNT=$(ls agents/ | wc -l)
  
  git tag -a "$TAG" -m "Monthly brain snapshot — ${MONTH}. Skills: ${SKILL_COUNT}. Agents: ${AGENT_COUNT}."
  git push origin "$TAG"
  ```

## Tag Format
```
brain-YYYY-MM

Example: brain-2026-03

Message: "Monthly brain snapshot — 2026-03. Skills: 36. Agents: 3."
```

**Stored in:** GitHub repo: github.com/suhailtajshaik/brain

## Recovery Process
If you need to restore from a monthly tag:
```bash
cd /home/r2d2/brain

# List all tags
git tag -l

# Checkout a specific month
git checkout brain-2026-02  # February snapshot

# Or reset to that point
git reset --hard brain-2026-02
```

## Monitoring
- **Health Check:** Tag exists on GitHub + contains correct metadata
- **Failure Modes:**
  - Git sync fails → script fails gracefully
  - GitHub unreachable → tag created locally but not pushed
  - Insufficient permissions → push fails
- **Alert Threshold:** If tag not pushed, notify Suhail (manual push needed)

## Integration
- **Part of:** Brain backup + disaster recovery strategy
- **Depends on:** Git + GitHub + brain/ directory + sync.sh
- **Triggered by:** Cron on 1st of month 6 AM
- **Coordinates with:** Notion brain sync (also Fridays around this time)
- **No external delivery** — just git tagging

## Benefits
1. **Immutable snapshots** — Can't accidentally overwrite old state
2. **Version history** — Know exactly what the brain knew in Feb vs Mar
3. **Recovery plan** — Gives us a defined rollback procedure
4. **Audit trail** — Each tag shows skill/agent count over time

## Files
- **Brain repo:** `/home/r2d2/brain/`
- **Sync script:** `/home/r2d2/brain/sync.sh`
- **GitHub:** `github.com/suhailtajshaik/brain`

## Maintenance
- **Last updated:** 2026-03-22 (ClawFlows launch)
- **Previous tags:** None (first month of system)
- **Next tag:** 2026-04-01

---

**Cron Job ID:** `9251b216-a9b6-4cb0-a35b-5e85ccec23b7`  
**Created:** 2026-03-06  
**Type:** Monthly immutable snapshot + recovery point
