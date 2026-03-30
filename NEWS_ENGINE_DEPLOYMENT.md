# News Engine Deployment — Dev Testing (March 30, 2026)

## 🚀 Setup Complete

**Parallel Pipelines Live:**
- ✅ **Production:** https://news.suhailtaj.cloud (Maxwell pipeline, 5 AM & 10 AM EST)
- ✅ **Dev:** https://news-dev.suhailtaj.cloud (News Engine, 11 AM EST)

## Architecture

```
PRODUCTION (Maxwell):
  5 AM EST ──→ generate-newspaper.py ──→ Maxwell agent ──→ news.suhailtaj.cloud
  10 AM EST ──→ (same pipeline)
  
DEV (News Engine):
  11 AM EST ──→ generate-dev-edition.py ──→ News orchestrator ──→ news-dev.suhailtaj.cloud

Both mount same archive:
  /home/r2d2/projects/news-site/public/archive/YYYY/MM/DD/
  → data.json (articles)
  → headlines-today.pdf
  → headlines-today.mp3
```

## What's Different

### Maxwell Pipeline (Production)
- **Speed:** 60-90 seconds
- **Articles:** 18-24 real articles
- **Sources:** 6-12 sources per article
- **Audio:** ~75 seconds
- **File Size:** ~587 KB
- **Verification:** Real RSS feeds + Claude editing

### News Engine Pipeline (Dev)
- **Speed:** 3-5 minutes (more analysis)
- **Articles:** 100+ articles
- **Sources:** 50+ real sources
- **Audio:** 3-5 minutes
- **File Size:** 1-2 MB
- **Verification:** Research + Fact-check + Intent analysis

## Cron Schedule

```
5:00 AM  → Maxwell prod edition
10:00 AM → Maxwell prod edition (daily backup)
11:00 AM → News-engine dev edition (parallel testing)
```

**Logs:**
- Maxwell: `/home/r2d2/tools/.guardian-logs/newspaper.log`
- News-engine: `/home/r2d2/tools/.guardian-logs/news-engine-dev.log`

## How to Test

### View Results

**Production (Maxwell):**
```
https://news.suhailtaj.cloud/archive/2026/03/31/
```

**Dev (News Engine):**
```
https://news-dev.suhailtaj.cloud/archive/2026/03/31/
```

Both show:
- `data.json` - Article list
- `headlines-today.pdf` - PDF newspaper
- `headlines-today.mp3` - Audio briefing

### Compare Quality

After next 11 AM generation:
1. Check prod: `curl https://news.suhailtaj.cloud/archive/2026/03/31/data.json | jq '.articles | length'`
2. Check dev: `curl https://news-dev.suhailtaj.cloud/archive/2026/03/31/data.json | jq '.articles | length'`
3. Compare article counts (should be 18-24 vs 100+)

### Monitor Logs

```bash
# Watch Maxwell production
tail -f /home/r2d2/tools/.guardian-logs/newspaper.log

# Watch News-engine dev
tail -f /home/r2d2/tools/.guardian-logs/news-engine-dev.log
```

## Docker Containers

**Prod + Dev both running:**
```bash
docker ps | grep news-site
```

Output:
```
news-site       → port 3333 (production, news.suhailtaj.cloud)
news-site-dev   → port 3334 (dev, lab.suhailtaj.cloud/the-headlines-today-dev/)
```

Both mount the same archive directory (read-only).

## Testing Timeline

**Tomorrow (March 31):**
- 5:00 AM: Maxwell generates prod edition
- 10:00 AM: Maxwell generates backup edition
- 11:00 AM: News-engine generates dev edition

**Compare at 11:30 AM:**
- Check both URLs
- Compare article counts
- Check audio duration
- Verify PDF quality

## Decision Points

### If News-Engine Quality is Better:
```
1. Run news-engine alongside Maxwell for 1 week
2. Verify stability and reliability
3. Switch cron: Replace Maxwell with news-engine in prod
4. Keep Maxwell config as backup
```

### If Maxwell is Sufficient:
```
1. Keep Maxwell in production (proven, stable)
2. Keep news-engine dev for future:
   - Test new RSS sources
   - Test verification improvements
   - Explore fact-checking enhancements
3. Switch when improvements are proven
```

### If Both are Needed:
```
1. Maxwell for daily prod (fast, reliable)
2. News-engine for extended edition (comprehensive analysis)
3. Mix outputs: Quick summary + Deep dive
```

## Next Steps

1. **Monitor first automated run** (11 AM today or tomorrow)
2. **Check logs** for any errors
3. **Compare quality metrics** (article count, audio length, sources)
4. **Make go/no-go decision** on news-engine for production

## Rollback Plan

If news-engine fails:
- Production continues on Maxwell (no disruption)
- Dev can be debugged independently
- Guardian monitors both and alerts on failures

**No risk to production.** Dev runs in parallel.

---

**Status:** 🟢 READY FOR TESTING
**Next Run:** 11 AM EST (dev), 5 AM EST (prod)
**Deployment Date:** March 30, 2026
