# Workflow: Daily Newspaper Generation

**ID:** r2d2:daily-newspaper  
**Category:** syncing  
**Enabled:** true  
**Cron:** `0 5 * * *` (daily at 5 AM EST)  
**Timezone:** America/New_York  

## Purpose
Generate a personalized newspaper for Suhail from RSS feeds (BBC, Reuters, AP, Times of India, HackerNews, NDTV, CNN, The Guardian). Deduplicates articles, curates sections, outputs structured JSON + PDF + audio.

**Deliverable:** PDF + MP3 sent to WhatsApp by 5:30 AM

## Schedule
- **Frequency:** Daily at 5 AM EST
- **Timezone:** America/New_York (EST/EDT)
- **Next Run:** Tomorrow, 5 AM (~20h 55m)
- **Last Run:** Yesterday 5 AM (failed)
- **Status:** ⚠️ **ERROR** (WhatsApp listener offline)

## Execution
- **Agent:** R2D2 (isolated session)
- **Timeout:** 300 seconds
- **Script:** `node /home/r2d2/generate-newspaper.js`
- **Output:** JSON data → `/home/r2d2/newspapers/YYYY/MM/DD/data.json`

## Pipeline Steps
1. **Fetch** — Pull articles from 8 RSS feeds
2. **Deduplicate** — Remove duplicate headlines + URLs
3. **Curate** — Organize by section (Business, Technology, Headlines, etc.)
4. **Generate** — Create JSON structure
5. **PDF** — Convert to styled PDF using headlines-today-pdf.js
6. **Audio** — Generate MP3 using TTS (gTTS)
7. **Deploy** — Upload to news-site web server
8. **Notify** — Send PDF + audio to Suhail via WhatsApp

## Monitoring
- **Data freshness:** JSON timestamp must be within 5 min of generation time
- **PDF generation:** Size should be 2-5 MB
- **Audio quality:** MP3 should be 15-30 MB (22 articles × ~1min each)
- **Deployment:** HTTP 200 on news-site container
- **Delivery:** WhatsApp message must succeed

## Issues & Troubleshooting
**Current Issue:** Last run failed with:
```
Error: No active WhatsApp Web listener (account: default).
Start the gateway, then link WhatsApp with: openclaw channels login --channel whatsapp --account default.
```

**Root cause:** WhatsApp gateway disconnected or not running.

**Fix:** Run:
```bash
openclaw gateway status
openclaw channels login --channel whatsapp --account default
```

**Guardian monitoring:** Watches for delivery failures + auto-restarts on consecutive errors

## Files
- **Script:** `/home/r2d2/generate-newspaper.js`
- **Output:** `/home/r2d2/newspapers/YYYY/MM/DD/data.json` + `.pdf` + `.mp3`
- **Web:** `/home/r2d2/news-site/` (deployed to nginx)
- **Logs:** `/home/r2d2/logs/newspaper-generation.log`

## Integration
- **Part of:** "The Headlines Today" project
- **Depends on:** Internet connectivity, RSS feed availability, WhatsApp account
- **Triggered by:** Cron daily at 5 AM
- **Delivers to:** WhatsApp (+14699941765)
- **Monitored by:** Guardian (every 5 min) + Notion sync (weekly)

## Maintenance
- **Last updated:** 2026-03-19 (WhatsApp delivery issue identified)
- **Next action:** Restart WhatsApp gateway
- **Known limitations:** Only works when gateway is running (can't auto-restart gateway from cron)

---

**Cron Job ID:** `67d04163-0947-43c6-8a8f-407e5ad00bb6`  
**Created:** 2026-03-15  
**Last Status Change:** 2026-03-22 (7 consecutive errors)
