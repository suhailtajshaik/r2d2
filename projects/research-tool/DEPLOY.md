# Deploy Research Tool

**Standalone web research application — Ready for use**

---

## Quick Start (60 seconds)

```bash
cd /home/r2d2/projects/research-tool

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Test it
python3 main.py --story "breaking news" --show-browser

# That's it!
```

---

## Use It

### Single Story

```bash
python3 main.py --story "Trump resigns" --date 2026-03-16
```

**Output:** `research_results.json`

### Batch Processing

```bash
# Create stories file
echo "Story 1" > stories.txt
echo "Story 2" >> stories.txt
echo "Story 3" >> stories.txt

# Research all
python3 main.py --file stories.txt --output results/

# Check output
ls results/
cat results/result_001.json
```

### Show Browser Window

```bash
python3 main.py --story "..." --show-browser
```

### Verbose Logging

```bash
python3 main.py --story "..." --verbose
```

---

## Integration with News Engine

Once research-tool is tested, integrate into news-engine:

```python
# news_engine/research.py
from research_tool import ResearchEngine

class PerplexityResearcher:
    def research(self, story):
        engine = ResearchEngine(browser='chromium', headless=True)
        result = engine.research(story.title, story.date)
        engine.close()
        
        return {
            'corroboration': result['corroboration']['sources'],
            'timeline': result['timeline'],
            'contradictions': result['contradictions'],
            'primary_source': result['primary_source']['outlet'],
        }
```

Then test full pipeline:

```bash
cd /home/r2d2/projects/news-engine
python3 main.py --dry-run --verbose
```

---

## What It Does

1. **Search** — Google search for story headline
2. **Scrape** — Open each result, extract full article text
3. **Analyze** — Build timeline, find contradictions
4. **Output** — JSON with corroboration, timeline, contradictions, confidence

---

## Output Example

```json
{
  "story": "Trump resigns",
  "corroboration": {
    "sources": ["BBC", "Reuters", "AP", "CNN"],
    "count": 4,
    "coverage_level": "widespread"
  },
  "timeline": [
    {
      "date": "2026-03-16",
      "outlet": "BBC",
      "headline": "US Official Resigns"
    }
  ],
  "contradictions": [],
  "primary_source": {
    "outlet": "BBC",
    "date": "2026-03-16"
  },
  "analysis": {
    "story_verified": true,
    "confidence": 0.95,
    "narrative_consistency": "high"
  }
}
```

---

## Files

```
/home/r2d2/projects/research-tool/
├── main.py                    # Run this
├── requirements.txt           # pip install
├── config.yaml               # Configuration
├── README.md                 # Full documentation
├── DEPLOY.md                 # This file
│
└── research_tool/
    ├── __init__.py
    ├── engine.py             # Core engine
    ├── scraper.py            # Web scraping
    └── analyzer.py           # Analysis
```

---

## Dependencies

- Python 3.10+
- playwright
- beautifulsoup4
- lxml
- python-dateutil

All in `requirements.txt`

---

## Troubleshooting

### "playwright not found"
```bash
pip install -r requirements.txt
playwright install chromium
```

### "Browser won't start"
```bash
playwright install chromium --with-deps
```

### "Timeout on slow internet"
Edit `config.yaml` and increase timeout values.

### "Memory usage too high"
Use `--parallel false` for batch processing.

---

## Next Steps

1. ✅ Install and test locally
2. ✅ Research 3-5 real stories
3. ✅ Verify output quality
4. ✅ Integrate with news-engine
5. ✅ Generate first real newspaper

---

**That's it. Ready to use.** 🚀
