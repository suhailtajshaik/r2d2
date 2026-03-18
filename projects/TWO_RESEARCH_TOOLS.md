# Two Research Tools — Complete Overview

**Two specialized research applications built: research-tool (generic) and newspaper-research (specialized)**

---

## 1. Research Tool v1.0 (Generic)

**Location:** `/home/r2d2/projects/research-tool/`

**Purpose:** Standalone web research using Playwright + Chrome
- Generic story research
- Corroboration extraction
- Timeline building
- Contradiction detection
- Confidence scoring

**Use Cases:**
- Standalone story verification
- Batch research processing
- Academic/journalistic investigation
- Fact-checking pipeline

**Output:** Full research metadata with article text, dates, contradictions

**CLI:**
```bash
python3 main.py --story "headline" --date 2026-03-16 --show-browser
```

**Files:**
```
research-tool/
├── main.py               # CLI
├── requirements.txt      # Dependencies
├── config.yaml          # Config
├── README.md            # Documentation
│
└── research_tool/
    ├── engine.py        # Orchestrator
    ├── scraper.py       # Web scraping (Playwright)
    └── analyzer.py      # Analysis
```

**Integration:**
```python
from research_tool import ResearchEngine

engine = ResearchEngine()
result = engine.research("headline", "2026-03-16")
```

---

## 2. Newspaper Research Tool v1.0 (Specialized)

**Location:** `/home/r2d2/projects/newspaper-research/`

**Purpose:** Research module for news-engine newspaper generation
- Optimized for newspaper pipeline
- Confidence scoring for publish decisions
- Newspaper-specific output format
- Batch processing for daily editions

**Use Cases:**
- Verify RSS feed stories before publication
- Build research data for newspaper articles
- Feed corroboration data to fact-checker
- Provide timeline for story context

**Output:** Newspaper-ready research with confidence, publish decision

**CLI:**
```bash
# Single story
python3 main.py --headline "..." --date 2026-03-16 --source BBC --section "World News"

# Batch from feed
python3 main.py --feed stories.json --output results/ --parallel true
```

**Files:**
```
newspaper-research/
├── main.py               # CLI
├── requirements.txt      # Dependencies
├── config.yaml          # Config
├── README.md            # Documentation
│
└── newspaper_research/
    ├── researcher.py    # Main class
    └── __init__.py
```

**Integration:**
```python
from newspaper_research import NewspaperResearcher

researcher = NewspaperResearcher()
result = researcher.research_story(
    headline="...",
    date="2026-03-16",
    source="BBC",
    section="World News"
)

if result['metadata']['publish_decision']:
    # Safe to publish
```

---

## Differences

| Aspect | research-tool | newspaper-research |
|--------|---------------|-------------------|
| **Purpose** | Generic web research | Newspaper-specific |
| **Use** | Standalone or as library | Integration with news-engine |
| **Output** | Full research metadata | Newspaper-ready format |
| **Publish Decision** | Confidence score | publish_decision flag |
| **Output Format** | Generic research | Newspaper schema |
| **Configuration** | Generic search config | Newspaper min_confidence, require_sources |

---

## Integration Flow

### News Engine Pipeline

```
RSS Feeds
    ↓
[News Engine]
    ├─ Fetch (FeedsManager)
    ├─ Research (newspaper-research)
    │   ├─ Search + Scrape
    │   ├─ Timeline extraction
    │   ├─ Contradiction detection
    │   └─ Confidence scoring
    ├─ Fact-Check (FactChecker)
    ├─ Intent Analysis (IntentExtractor)
    └─ Synthesize & Decide (Analyzer)
    ↓
Verified Edition
```

### Code Integration

```python
# news_engine/research.py
from newspaper_research import NewspaperResearcher

class PerplexityResearcher:
    def __init__(self, config):
        self.researcher = NewspaperResearcher(config)
    
    def research(self, story):
        result = self.researcher.research_story(
            headline=story.title,
            date=story.date,
            source=story.source,
            section=story.section
        )
        
        return {
            'corroboration': result['sources'],
            'timeline': result['timeline'],
            'contradictions': result['contradictions'],
            'primary_source': result['primary_source']['outlet'],
        }
```

---

## Installation Summary

### Research Tool
```bash
cd /home/r2d2/projects/research-tool
pip install -r requirements.txt
playwright install chromium
```

### Newspaper Research Tool
```bash
cd /home/r2d2/projects/newspaper-research
pip install -r requirements.txt
playwright install chromium
```

---

## Testing

### Research Tool

```bash
cd /home/r2d2/projects/research-tool

# Single story
python3 main.py --story "Trump resigns" --show-browser

# Batch
python3 main.py --file stories.txt --output results/
```

### Newspaper Research Tool

```bash
cd /home/r2d2/projects/newspaper-research

# Single story
python3 main.py --headline "Trump resigns" --date 2026-03-16 --source BBC

# Batch
python3 main.py --feed stories.json --output results/ --parallel true
```

---

## When to Use Each

### Use research-tool for:
- One-off research
- Fact-checking investigations
- General corroboration research
- Academic/journalistic work

### Use newspaper-research for:
- Newspaper publication workflow
- Daily edition generation
- RSS feed verification
- Batch story processing
- Publish/no-publish decisions

---

## Dependencies

Both tools require:
- Python 3.10+
- Playwright 1.40+
- beautifulsoup4 (HTML parsing)
- lxml (XML parsing)
- python-dateutil (date parsing)
- pydantic (data validation)

newspaper-research also imports research-tool internally.

---

## Next Steps

1. ✅ Test research-tool independently
2. ✅ Test newspaper-research independently
3. ✅ Integrate newspaper-research into news-engine
4. ✅ Generate first real newspaper edition

---

## Documentation

- **research-tool:** README.md, DEPLOY.md
- **newspaper-research:** README.md, DEPLOY.md
- **Integration:** Each README has integration examples

---

**Two tools. One pipeline. Full newspaper generation system ready.** 🚀
