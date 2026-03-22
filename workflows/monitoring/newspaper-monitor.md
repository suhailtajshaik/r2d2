# Workflow: Guardian Newspaper Monitor

**ID:** guardian:newspaper-monitor  
**Category:** monitoring  
**Enabled:** true  
**Cron:** `*/5 * * * *` (every 5 minutes)  
**Timezone:** America/New_York  

## Purpose
Guardian is the 24/7 watchdog for the newspaper pipeline. This workflow checks data freshness, PDF/audio generation, web deployment status, and cron job health. Auto-fixes common issues (regenerate missing files, rebuild site, restart containers).

**Impact:** If newspaper pipeline breaks, Guardian detects within 5 minutes and auto-heals.

## Schedule
- **Frequency:** Every 5 minutes
- **Timezone:** America/New_York (EST/EDT)
- **Next Run:** Auto-calculated
- **Last Run:** ~30s ago
- **Status:** ✅ Active

## Execution
- **Agent:** Guardian (isolated session)
- **Timeout:** 300 seconds
- **Message:**
  ```
  You are Guardian, the watchdog. Run the newspaper pipeline monitor:

  bash /home/r2d2/tools/guardian-newspaper-monitor.sh

  This checks: data.json freshness, PDF size, audio quality, web deployment, cron job status. 
  Auto-fixes any issues found. Report results concisely.
  ```

## Monitoring
- **Health Check:** File timestamps for `/home/r2d2/newspapers/YYYY/MM/DD/data.json`, `headlines-today.pdf`, `headlines-today.mp3`
- **Deployment Check:** HTTP 200 on news-site container
- **Failure Modes:**
  - data.json >30 min old → regenerate
  - PDF/audio missing → rebuild
  - Web site down → restart container
  - Cron job disabled → alert (manual fix needed)
- **Remediation:** Run `guardian-newspaper-monitor.sh` with auto-fix flag
- **Alert Threshold:** 2 consecutive failures → notify Suhail

## Logs
- Stdout: Guardian agent output (concise summary)
- Script output: `/home/r2d2/logs/guardian-newspaper-monitor.log`
- Last error: (none — all healthy)

## Integration
- **Part of:** Newspaper pipeline (5 AM generation + continuous monitoring)
- **Depends on:** `guardian-newspaper-monitor.sh` script + Docker containers
- **Triggered by:** Cron every 5 minutes
- **Delivers to:** WhatsApp (+14699941765) on errors only

## Maintenance
- **Script location:** `/home/r2d2/tools/guardian-newspaper-monitor.sh`
- **Config:** `/home/r2d2/docker/guardian-config.yaml`
- **Last updated:** 2026-03-20 (fixed filename check)
- **Known issues:** None

---

**Cron Job ID:** `ee5fae90-ccca-4766-888b-290a1a0dfb21`  
**Created:** 2026-03-19  
**Last Status Change:** 2026-03-20 (filename fix)
