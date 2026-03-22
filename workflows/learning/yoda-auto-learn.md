# Workflow: Yoda Auto-Learn Sync

**ID:** yoda:auto-learn  
**Category:** learning  
**Enabled:** true  
**Cron:** `0 2,8,14,20 * * *` (2 AM, 8 AM, 2 PM, 8 PM EST)  
**Timezone:** America/New_York  

## Purpose
Yoda's knowledge base auto-updates from brain/lessons/ and brain/docs/ directories. This workflow synthesizes new learning from experience, architecture decisions, and best practices into a living reference system.

**Impact:** Yoda stays current with latest lessons, reducing repeated mistakes and improving code review quality.

## Schedule
- **Frequency:** 4 times daily (2 AM, 8 AM, 2 PM, 8 PM EST)
- **Timezone:** America/New_York (EST/EDT)
- **Next Run:** +10 hours
- **Last Run:** 8 AM today (6m ago) ✅
- **Status:** ✅ Active

## Execution
- **Type:** systemEvent (main session)
- **Payload:** `"Yoda auto-learn sync running (2 AM, 8 AM, 2 PM, 8 PM EST)"`
- **No timeout** (runs in background, doesn't block)

## Knowledge Base
Yoda maintains a living knowledge base with:
- **code-review-checklist.md** — Quality standards, security, performance
- **api-architecture-mistake.md** — Learned lessons from production issues
- **Architecture docs** — Design patterns, microservices, databases
- **Training insights** — Language models, prompt engineering, agentic systems
- **Evolution log** — Weekly self-review improvements

**Storage:** `/home/r2d2/brain/lessons/` (synced to Yoda's context automatically)

## Monitoring
- **Health Check:** Files exist in brain/lessons/ and brain/docs/
- **Knowledge freshness:** KB should reflect code written in last 6 hours
- **Failure Modes:**
  - brain/ directory missing → alert (critical, no backup)
  - Stale knowledge (>24h old) → not critical but suboptimal
- **Remediation:** Manual — ensure brain repo is cloned and synced
- **Alert Threshold:** Never (silent, knowledge-building task)

## Integration
- **Part of:** R2D2's learning loop (self-improvement system)
- **Depends on:** brain/lessons/ directory + brain/docs/ structure
- **Triggered by:** Cron 4x daily
- **Delivers to:** Main session (no external notifications)
- **Used by:** Yoda code review agent + R2D2 decision-making

## Maintenance
- **Last reviewed:** 2026-03-20
- **Knowledge base size:** 240K+ characters across 7+ files
- **Gap areas:** AI agents, voice multimodal, video synthesis
- **Next sync:** Tomorrow 2 AM

---

**Cron Job ID:** `7204a7dc-3a01-49c2-b30d-e4f70c522f23`  
**Created:** 2026-03-20  
**Type:** Silent background learning (no interruptions)
