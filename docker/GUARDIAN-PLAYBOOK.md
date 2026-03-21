# Guardian Playbook — Infrastructure & Application Watchdog
**Last Updated:** March 20, 2026
**Version:** v4 (Enhanced Self-Healing with Predictive Maintenance)
**Suhail's Directive:** Guardian owns all infrastructure, cron jobs, and any new applications going forward.

---

## What's New in v4 (March 20, 2026)

### 🔄 Smarter Retry Logic
- **Exponential backoff:** 1s → 2s → 4s instead of fixed delays
- **Circuit breaker pattern:** After 5 consecutive failures, Guardian stops retrying and alerts instead (avoids thrashing)
- **Per-service tracking:** Maintains state of failures, remediation attempts, and success rates

### 📋 Enhanced Diagnostics
- **Pre-restart log capture:** Before restarting a container, Guardian captures its logs for analysis
- **System state snapshots:** Records disk usage, memory, and top processes before/after remediation
- **Diagnostic reports:** JSON files saved to `/tmp/guardian/diagnostics/` for human review
- **Failure attribution:** Each check knows WHY it failed (not just that it did)

### 📈 Predictive Maintenance
- **Trend analysis:** Monitors disk usage growth over time
- **Early warnings:** Alerts when disk will fill at current growth rate (e.g., "will fill in 3 days")
- **Metric history:** Keeps 30-day history of system metrics for trend detection
- **Actionable suggestions:** Recommends preventive actions (cleanup logs, archive newspapers)

### 🧠 Self-Learning System
- **Remediation tracking:** Records which actions work best for each failure type
- **Success rates:** Calculates success % for each (service, action) pair
- **Memory updates:** Writes learnings to `/home/r2d2/.openclaw/workspace/memory/guardian-learning.md`
- **Human-readable reports:** Shows common issues, effective remediations, and predictions

### 📢 Enhanced Notifications
- **Alert batching:** Groups issues from one cycle instead of spamming individual messages
- **Deduplication:** Removes duplicate alerts within 5-minute window
- **Severity levels:** CRITICAL alerts only sent when threshold exceeded (default: >2 issues)
- **False alarm tracking:** Counts self-healed issues that never reach Suhail

### 🛡️ Graceful Degradation
- **Non-critical service protection:** If a service fails 3+ times, Guardian disables its checks
- **Critical service prioritization:** nginx, news-site, and Guardian itself always checked
- **Manual overrides:** Suhail can reset service state or disable/enable checks
- **Failure isolation:** One service's failures don't affect others

---

## Guardian's Mission
Guardian is a 24/7 self-healing watchdog that:
- **Monitors** all VPS infrastructure, Docker containers, cron jobs, and applications
- **Auto-fixes** common failures without human intervention
- **Alerts** only when critical issues persist (not chatty)
- **Learns** from every issue to improve future resilience

**Philosophy:** If it's broken, Guardian fixes it. If it's new, Guardian watches it.

---

## How Guardian Works

### Detection (Every 5 Minutes)
Guardian runs scheduled checks across:
1. **Docker containers** — running, healthy, resource usage
2. **Cron jobs** — status, last run, error count
3. **Web applications** — HTTP endpoints responding, file sizes correct
4. **File system** — disk usage, critical files present and fresh
5. **Logs** — error patterns, warnings
6. **System metrics** — disk/memory trends for predictive maintenance

### Remediation (Automatic with Intelligence)
When Guardian detects a failure, it runs remediation with:
- **Exponential backoff retry:** 1s, 2s, 4s delays between attempts
- **Circuit breaker:** If 5+ consecutive failures, escalate to alert instead of retrying
- **Diagnostics capture:** Before restart, capture logs and system state
- **Verification:** Confirm fix worked before marking success
- **Learning:** Track which fixes work best for each service/failure combo

Remediation actions:
- **Restart:** Docker container, cron job, service
- **Rebuild:** React site, Python project
- **Resync:** Files from source to destination
- **Regenerate:** Missing outputs (newspaper, PDF, audio)
- **Retry:** Failed operations with exponential backoff

### Alerting (Smart, Not Chatty)
Guardian is silent by default. It alerts Suhail when:
- **Batched alerts:** >2 issues detected in one check cycle (not per-issue)
- **Circuit breaker open:** Service has 5+ consecutive failures
- **Predictive alert:** System trending toward failure (e.g., disk filling up)
- **Remediation failed:** Auto-fix didn't work after exponential retries
- **Manual intervention needed:** Issue requires human action

Deduplication: Same issue won't be alerted twice within 5 minutes

---

## Adding a New Application to Guardian

### Step 1: Define the Application (YAML)
```yaml
app_name:
  name: "Human-readable name"
  description: "What it does"
  critical: true  # Set to false if not essential
  
  checks:
    - name: "Check name"
      type: "file|http|cron|docker|log"  # Type of check
      
      # For file checks:
      path: "/path/to/file"
      min_size: 10240  # Bytes
      max_age: 86400   # Seconds (24h)
      
      # For HTTP checks:
      url: "https://example.com/endpoint"
      expected_status: 200
      timeout: 10  # Seconds
      
      # For cron checks:
      job: "job-name"
      
      # For Docker checks:
      container: "container-name"
      
      # For log checks:
      source: "/path/to/log"
      search: "regex pattern"
      
      interval: 300  # Check every 300 seconds
      alert_if: "condition"  # missing|stale|offline|unhealthy
```

### Step 2: Define Remediation Steps
```yaml
  remediation:
    trigger: "Condition that triggers remediation"
    max_retries: 3
    backoff: exponential  # or linear, fixed
    steps:
      - action: "restart|rebuild|resync|regenerate|custom"
        target: "what to target"
        timeout: 300
        rollback: "Previous version/state if it fails"
```

### Step 3: Register with Guardian
Add the configuration to `/home/r2d2/docker/guardian-config.yaml` under `watchlist:`

### Step 4: Test
Run Guardian manually to verify the checks work:
```bash
bash /home/r2d2/tools/guardian-newspaper-monitor.sh
```

---

## Current Applications Guardian Monitors

### 1. Newspaper Pipeline (The Headlines Today)
- **What:** Daily newspaper generation (119 articles, PDF, audio)
- **Checks:** Data freshness, PDF/audio size, web API response, cron job status
- **Interval:** Every 5 minutes
- **Remediation:** Regenerate data, rebuild site, restart cron job
- **Critical:** Yes
- **Config:** See `guardian-config.yaml` → `newspaper_pipeline`

### 2. Docker Infrastructure
- **What:** Container health, resource usage, auto-cleanup
- **Checks:** Container running, CPU/memory usage, disk space
- **Interval:** Every 5 minutes
- **Remediation:** Restart container, prune images, expand disk
- **Critical:** Yes
- **Config:** Docker event listener + cleanup tasks

### 3. Cron Jobs
- **What:** All scheduled tasks (Maxwell, Yoda, monthly tags, etc.)
- **Checks:** Job enabled, last run successful, error count
- **Interval:** Every hour
- **Remediation:** Restart job, clear error state, retry generation
- **Critical:** Depends on job
- **Config:** Cron health check in `guardian-newspaper-monitor.sh`

---

## Guardian's Standard Operating Procedures (SOPs)

### SOP-001: Container Restart
**When:** Docker container unhealthy or not responding
**How:**
```bash
docker restart <container-name>
sleep 10
docker ps | grep <container-name>
```
**Verify:** Check health status, verify service responding
**Rollback:** If service not responding after 3 retries, alert Suhail

### SOP-002: File Regeneration
**When:** Critical file missing or stale
**How:**
```bash
cd /path/to/app
node generate-output.js  # or python, make, etc.
verify output exists and has correct size
```
**Verify:** Check file exists, size >min, timestamp recent
**Rollback:** If generation fails, try previous version

### SOP-003: Site Rebuild
**When:** Web app not responding, files missing
**How:**
```bash
cd /path/to/app
npm run build  # or equivalent
# Copy to deployment location
# Restart web server
```
**Verify:** HTTP 200 response, files served correctly
**Rollback:** Restore previous build, restart

### SOP-004: File Sync
**When:** Files out of sync between source and destination
**How:**
```bash
rsync -avz --delete /source/ /destination/
```
**Verify:** Verify file count and sizes match
**Rollback:** Reverse sync if verification fails

### SOP-005: Log Analysis
**When:** Looking for error patterns
**How:**
```bash
grep -i "error|failed|critical" /var/log/app.log | tail -20
```
**Report:** Frequency, pattern, first occurrence

---

## Guardian's Alert Levels

| Level | Condition | Action | Notify |
|-------|-----------|--------|--------|
| **Silent** | Single issue in check | Auto-fix, log it | No |
| **Warning** | 3+ issues in 24h | Auto-fix, log it, note pattern | Memory log only |
| **Critical** | >2 issues in one check cycle OR remediation failed | Auto-fix if possible, escalate | Suhail + log |
| **Manual** | Auto-fix impossible | Detailed alert with instructions | Suhail + detailed log |

---

## Guardian's Learning System (v4)

### Failure Tracking
Guardian maintains persistent state in `/tmp/guardian/state.json`:
```json
{
  "services": {
    "newspaper": {
      "consecutive_failures": 0,
      "total_failures": 3,
      "remediation_attempts": 2,
      "remediation_success": 2,
      "success_rate": "100%",
      "disabled": false,
      "failed_checks": [
        {
          "check": "data-file",
          "error": "Too small (4832 bytes)",
          "time": "2026-03-20T07:30:45"
        }
      ]
    }
  },
  "circuit_breakers": {},
  "remediation_history": [
    {
      "service": "newspaper",
      "action": "regenerate",
      "success": true,
      "time": "2026-03-20T07:31:12"
    }
  ]
}
```

### Learning Output
Guardian writes curated insights to `/home/r2d2/.openclaw/workspace/memory/guardian-learning.md`:
- **Service health summary:** Status, failure count, remediation success rate
- **Common issues:** Top issues detected in last 24h with occurrence count
- **Effective remediations:** Which actions have highest success rates
- **Predictive alerts:** Disk fill predictions, memory trends, etc.

### Metrics History
Guardian tracks system metrics in `/tmp/guardian/metrics-history.json`:
- Disk usage %, memory %, container health
- Kept for 30 days for trend analysis
- Used to predict failures before they happen

### Diagnostics Archive
Every remediation creates a detailed report in `/tmp/guardian/diagnostics/`:
```
newspaper_restart_20260320_073145.json
{
  "service": "newspaper",
  "action": "restart",
  "timestamp": "2026-03-20T07:31:45",
  "snapshot_before": {
    "disk": {"used": "45G", "available": "55G", "percent": "45%"},
    "memory": {"total": "16G", "used": "8G", "available": "8G"},
    "top_processes": [...]
  },
  "logs_before": "..container logs before restart..",
  "snapshot_after": {...}
}
```

### Over Time
Guardian identifies patterns for human investigation:
- "Audio fails every Tuesday at 5:15 AM" → Scheduled maintenance interfering?
- "Web deployment fails after large rebuilds" → Disk space? Memory pressure?
- "Container X crashes every 48h" → Memory leak? Resource limit too tight?

### Continuous Improvement
Guardian auto-updates `/home/r2d2/.openclaw/workspace/memory/guardian-learning.md` with:
- Top 5 common issues
- Most effective remediation actions
- Failure rate trends
- Recommended preventive maintenance

---

## Deploying a New Application — Checklist

When you deploy a new app, Guardian needs:

- [ ] **App location** — Where does it live? (`/home/r2d2/projects/xyz`)
- [ ] **Health check** — How do you know it's working? (HTTP endpoint? File exists? Cron succeeds?)
- [ ] **Normal behavior** — What's the expected output? (File size range? Response time?)
- [ ] **Failure indicators** — What signals failure? (404? File size 0? Timeout?)
- [ ] **Remediation steps** — How to fix? (Restart? Rebuild? Resync?)
- [ ] **Criticality** — Is it business-critical? (Affects Suhail's workflow?)
- [ ] **Dependencies** — Does it depend on other apps or services?

**Format for new apps:**
```yaml
# Add to guardian-config.yaml
watchlist:
  my_new_app:
    name: "My New App"
    critical: true
    checks:
      - name: "Is it alive?"
        type: "http"
        url: "https://myapp.suhailtaj.cloud/health"
        expected_status: 200
        interval: 300
      - name: "Latest output"
        type: "file"
        path: "/home/r2d2/projects/my-app/output.json"
        min_size: 1024
        max_age: 86400
        interval: 300
    remediation:
      trigger: "checks failing"
      steps:
        - action: "rebuild"
          target: "/home/r2d2/projects/my-app"
        - action: "restart"
          target: "container: my-app-server"
```

**Then tell Guardian:**
```bash
# Add to cron or heartbeat
echo "Guardian: Monitor my_new_app per guardian-config.yaml"
```

---

## Contacting Guardian

**For status updates:**
```bash
bash /home/r2d2/tools/guardian-newspaper-monitor.sh
# View logs: /tmp/guardian-newspaper.log
```

**For new app monitoring:**
Update `guardian-config.yaml` + add check to monitoring script

**For issues:**
Guardian alerts Suhail automatically when critical. Check memory logs: `/home/r2d2/.openclaw/workspace/memory/guardian-alerts.log`

---

## Guardian's Permissions & Capabilities

Guardian can:
- ✅ Restart Docker containers
- ✅ Rebuild React/Node apps
- ✅ Run shell scripts and Python
- ✅ Regenerate files (newspaper, PDFs, audio)
- ✅ Restart cron jobs
- ✅ Sync files between directories
- ✅ Query HTTP endpoints
- ✅ Read logs and search patterns
- ✅ Write to memory logs

Guardian cannot (yet):
- ❌ Delete data (only overwrites with regenerated versions)
- ❌ Modify production databases
- ❌ Approve security-sensitive changes
- ❌ Escalate beyond WhatsApp alerts to Suhail

---

## Key v4 Improvements Summary

| Feature | v3 | v4 | Impact |
|---------|----|----|--------|
| Retry strategy | Fixed delays | Exponential backoff (1s → 2s → 4s) | Smarter about when to give up |
| Circuit breaker | None | 5+ failures → alert instead of retry | Prevents thrashing |
| Diagnostics | Logs only | Captures logs + system state + reports | Better troubleshooting |
| Trends | None | 30-day history, disk fill predictions | Prevents issues before they happen |
| Learning | None | Success rate tracking, memory updates | Gets better over time |
| Alerts | Per-issue | Batched + deduplicated | Less spam to Suhail |
| Non-critical services | Always monitored | Auto-disable after 3 failures | Isolates noisy services |

## Manual Commands

### Check Guardian Status
```bash
# View current state
cat /tmp/guardian/state.json | jq .

# View learning summary
cat /home/r2d2/.openclaw/workspace/memory/guardian-learning.md

# View recent logs
tail -50 /tmp/guardian/guardian.log

# Run Guardian manually (don't wait for cron)
python3 /home/r2d2/docker/guardian.py
```

### Reset Service State
```bash
# Clear all failures for a service (tell Guardian to forget and try again)
python3 << 'EOF'
import json
state = json.load(open('/tmp/guardian/state.json'))
state['services']['newspaper']['consecutive_failures'] = 0
state['services']['newspaper']['total_failures'] = 0
state['circuit_breakers'].pop('newspaper', None)
json.dump(state, open('/tmp/guardian/state.json', 'w'), indent=2)
print("✅ Reset newspaper service state")
EOF
```

### Disable/Enable Service Monitoring
```bash
# Disable monitoring for a service (Guardian won't check it)
python3 << 'EOF'
import json
state = json.load(open('/tmp/guardian/state.json'))
state['services']['newspaper']['disabled'] = True
json.dump(state, open('/tmp/guardian/state.json', 'w'), indent=2)
print("✅ Disabled newspaper monitoring")
EOF

# Re-enable
python3 << 'EOF'
import json
state = json.load(open('/tmp/guardian/state.json'))
state['services']['newspaper']['disabled'] = False
json.dump(state, open('/tmp/guardian/state.json', 'w'), indent=2)
print("✅ Enabled newspaper monitoring")
EOF
```

---

## Summary

Guardian v4 is your infrastructure autopilot with a brain. It:
- 🔄 **Retries smartly** with exponential backoff + circuit breaker
- 📋 **Diagnoses thoroughly** with logs and system snapshots
- 📈 **Predicts failures** before they happen
- 🧠 **Learns continuously** from every issue
- 📢 **Alerts intelligently** with batching and deduplication
- 🛡️ **Degrades gracefully** when services fail repeatedly

**The rule:** If Guardian can't auto-fix something after exponential retries, it escalates to you with full diagnostics.

---

**Maintenance:** Review `/home/r2d2/.openclaw/workspace/memory/guardian-learning.md` daily to spot patterns and trends.

Last updated: 2026-03-20
Guardian version: v4 (Python-based with ML-lite learning)
Repository: `/home/r2d2/docker/guardian.py`
