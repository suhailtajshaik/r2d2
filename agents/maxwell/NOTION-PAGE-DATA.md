# Maxwell Agent - Notion Page Data

**Already exists in Notion - verify these details are current**

Page ID: 324c2d43-b275-81bd-8845-d22737d4bda4

## Properties

### Type
Cron Job + Python

### Status
Running ✅ (Daily newspaper + 5 new workflows)

### Role
Senior news editor + multi-workflow reporting system

### Description
Maxwell is the editorial brain behind The Headlines Today newspaper and generates daily/weekly/monthly reports across multiple domains.

**Workflows:**
1. **Daily Newspaper** (5 AM EST) — 23 articles, PDF + audio
2. **Daily Market Analysis** (7 AM EST) — Stock/crypto/sentiment
3. **Weekly Research Report** (Sundays 8 AM EST) — Deep dives on trends
4. **Monthly Industry Report** (1st, 9 AM EST) — SaaS/AI landscape
5. **Project Status Report** (Fridays 5 PM EST) — Git commits + blockers
6. **Performance Analytics** (Daily 6 PM EST) — Uptime, costs, metrics

### Location
Source: `/home/r2d2/tools/generate-newspaper.py`
Workflows: `/home/r2d2/tools/maxwell-workflows.py`
Output: `/home/r2d2/newspapers/` & `/home/r2d2/reports/`

### Schedule

```
0 5 * * *  — Daily newspaper (5 AM EST)
0 7 * * *  — Daily market analysis (7 AM EST)
0 8 * * 0  — Weekly research (Sundays 8 AM EST)
0 9 1 * *  — Monthly industry report (1st, 9 AM EST)
0 17 * * 5 — Project status (Fridays 5 PM EST)
0 18 * * *  — Performance analytics (Daily 6 PM EST)
```

### Output

**Newspapers:** `/home/r2d2/newspapers/YYYY/MM/DD/`
- `data.json` — Article list
- `headlines-today.pdf` — Full edition
- `headlines-today.mp3` — Audio version (1.25x speed)

**Reports:** `/home/r2d2/reports/YYYY/MM/`
- Market analysis PDFs
- Research reports
- Industry analysis
- Project summaries

**News Site:** https://news.suhailtaj.cloud/

### Logs
- Newspaper: `/var/log/maxwell.log`
- Workflows: `/home/r2d2/brain/memory/maxwell_*.log`

### Features
- RSS feed aggregation (40+ sources)
- AI editorial filtering
- PDF generation
- Audio synthesis (gTTS)
- WhatsApp delivery
- Notion integration
- Trend analysis
- Sentiment detection

### Version
v2 (newspaper redesign) + Workflows v1 (5 new workflows)

### Created
Daily newspaper: 2026-03-05
Workflows: 2026-03-20

### Last Updated
2026-03-21 (workflows deployed)

### Related Agents
- Guardian — Infrastructure health
- Yoda — Knowledge synthesis
- Voice Agent — Read briefs aloud
