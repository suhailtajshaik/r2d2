# Guardian Agent - Notion Page Data

**Already exists in Notion - verify these details are current**

Page ID: 324c2d43-b275-81b4-bfc7-fb7219981909

## Properties

### Type
Docker Container

### Status
Running ✅ (3 days uptime)

### Role
24/7 infrastructure watchdog with predictive maintenance and self-learning

### Description
Guardian is a containerized watchdog that monitors infrastructure health, auto-remediates failures, and learns from every fix to improve future decisions.

**Features (v4):**
- Smart retry with exponential backoff
- Predictive maintenance (3-5 day forecasting)
- Self-learning (success rate tracking)
- Circuit breaker (stops after 5 consecutive failures)
- Comprehensive diagnostics (pre/post snapshots)
- Graceful degradation
- Alert batching and deduplication

### Location
Docker container: `r2d2-guardian`
Source: `/home/r2d2/docker/guardian.py`
Config: `/home/r2d2/docker/guardian-config.yaml`
Playbook: `/home/r2d2/docker/GUARDIAN-PLAYBOOK.md`

### Monitoring

**Checks (every 5 minutes):**
- OpenClaw status
- Container health
- Disk/memory usage
- SSL certificate validity
- Port availability
- Newspaper freshness
- Brain repo sync
- Notion accessibility
- In-flight agents

**Auto-fixes up to 3 attempts:**
- Restart failed containers
- Regenerate newspaper
- Cleanup disk space
- Trigger brain sync

### Configuration
File: `/home/r2d2/docker/guardian-config.yaml`

### Logs
- Location: `/home/r2d2/.openclaw/workspace/memory/guardian-alerts.log`
- Docker: `docker logs r2d2-guardian`

### Version
v4 - Enhanced with predictive maintenance and self-learning

### Created
2026-03-15

### Last Updated
2026-03-21 (v4 upgrade)

### Related Agents
- Yoda — Learning loop
- Maxwell — News generation
