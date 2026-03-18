# research.py Implementation Guide

**Task:** Convert stub to working web search integration

**Two Options:**
1. **Perplexity (web_search tool)** — Recommended, simpler
2. **Playwright + Chrome** — Advanced, more control

---

## Option 1: Perplexity (Recommended)

### How It Works

```python
from web_search import web_search

results = web_search(
    query="Trump resigns counterterrorism 2026",
    count=10,
    freshness="week"
)
# Returns list of search results
```

**Result Format:**
```python
[
    {
        'title': 'US Counterterrorism Official Resigns',
        'source': 'BBC',
        'url': 'https://...',
        'snippet': 'National Counterterrorism Center Director Joe Kent...',
        'published_date': '2026-03-16',
    },
    ...
]
```

### Implementation

```python
import logging
from typing import Dict, List
from datetime import datetime
from web_search import web_search

logger = logging.getLogger(__name__)

class PerplexityResearcher:
    def __init__(self, config):
        self.config = config
    
    def research(self, story) -> Dict:
        """
        Research a story using Perplexity web search.
        
        Args:
            story: RawStory object
        
        Returns:
            {
                'corroboration': ['BBC', 'Reuters', 'AP', ...],
                'timeline': [
                    {'date': '2026-03-16', 'outlet': 'BBC', 'claim': '...'},
                    {'date': '2026-03-17', 'outlet': 'Reuters', 'claim': '...'},
                ],
                'contradictions': [
                    'Admin claims Kent was not fired (vs resignation report)',
                ],
                'primary_source': 'BBC',
            }
        """
        logger.debug(f'Researching: {story.title[:50]}...')
        
        # Build search query
        query = self._build_query(story)
        logger.debug(f'Search query: {query}')
        
        # Search web
        results = web_search(
            query=query,
            count=self.config.max_results,  # 10
            freshness='week'  # Last week
        )
        
        if not results:
            logger.warning(f'No search results for: {story.title}')
            return self._empty_research()
        
        # Extract corroboration
        corroboration = self._extract_corroboration(results)
        
        # Extract timeline
        timeline = self._extract_timeline(results)
        
        # Extract contradictions
        contradictions = self._extract_contradictions(results)
        
        # Identify primary source
        primary_source = self._identify_primary_source(timeline, results)
        
        return {
            'corroboration': corroboration,
            'timeline': timeline,
            'contradictions': contradictions,
            'primary_source': primary_source,
        }
    
    def _build_query(self, story: str) -> str:
        """Build search query from story headline."""
        # Extract key words from headline
        words = story.title.split()[:5]  # First 5 words
        query = ' '.join(words)
        
        # Add year for recency
        if hasattr(story, 'date'):
            query += f' {story.date.year}'
        
        return query
    
    def _extract_corroboration(self, results: List) -> List[str]:
        """Extract outlet names from search results."""
        outlets = []
        for result in results:
            outlet = result.get('source', 'Unknown')
            if outlet not in outlets:
                outlets.append(outlet)
        
        return outlets[:10]  # Top 10 sources
    
    def _extract_timeline(self, results: List) -> List[Dict]:
        """Extract story evolution over time."""
        timeline = []
        
        for result in results:
            date = result.get('published_date')
            outlet = result.get('source')
            claim = result.get('snippet', '')[:200]  # First 200 chars
            
            if date:
                timeline.append({
                    'date': date,
                    'outlet': outlet,
                    'claim': claim,
                })
        
        # Sort by date
        timeline.sort(key=lambda x: x['date'])
        
        return timeline
    
    def _extract_contradictions(self, results: List) -> List[str]:
        """Identify contradictory claims between sources."""
        contradictions = []
        
        # Simple heuristic: look for conflicting language
        snippets = [r.get('snippet', '').lower() for r in results]
        
        # Check for common contradictions
        if any('fired' in s for s in snippets) and any('resigned' in s for s in snippets):
            contradictions.append('Some sources say "fired", others say "resigned"')
        
        if any('denies' in s for s in snippets) and any('confirms' in s for s in snippets):
            contradictions.append('Conflicting confirmations in reporting')
        
        # Look for quantitative disagreements
        numbers = []
        for snippet in snippets:
            # Extract numbers if present
            import re
            nums = re.findall(r'\d+', snippet)
            numbers.extend(nums)
        
        if numbers and len(set(numbers)) > 1:
            unique_nums = list(set(numbers))
            contradictions.append(f'Conflicting numbers reported: {", ".join(unique_nums)}')
        
        return contradictions
    
    def _identify_primary_source(self, timeline: List, results: List) -> str:
        """Identify which outlet reported story first."""
        if not timeline:
            return results[0].get('source', 'Unknown') if results else 'Unknown'
        
        # First date in timeline
        first = timeline[0]
        return first.get('outlet', 'Unknown')
    
    def _empty_research(self) -> Dict:
        """Return empty research result."""
        return {
            'corroboration': [],
            'timeline': [],
            'contradictions': [],
            'primary_source': 'Unknown',
        }
```

---

## Option 2: Playwright + Chrome (Advanced)

Use if you need to extract full article text, metadata, etc.

```python
from playwright.sync_api import sync_playwright
from typing import Dict, List

class PlaywrightResearcher:
    def research(self, story) -> Dict:
        """Research using Playwright browser."""
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Search Google
            page.goto('https://www.google.com')
            page.fill('input[name="q"]', story.title)
            page.press('input[name="q"]', 'Enter')
            page.wait_for_load_state('networkidle')
            
            # Extract results
            results = page.query_selector_all('div.g')
            
            # Process each result
            corroboration = []
            timeline = []
            for result in results[:10]:
                title = result.query_selector('h3')?.inner_text()
                link = result.query_selector('a')?.get_attribute('href')
                # Extract date, outlet, etc.
                ...
            
            browser.close()
            
            return {
                'corroboration': corroboration,
                'timeline': timeline,
                'contradictions': [],
                'primary_source': corroboration[0] if corroboration else 'Unknown',
            }
```

**Pros:**
- Full control over scraping
- Can extract full article text
- Access to JavaScript-rendered content

**Cons:**
- Slower (needs to load pages)
- Browser overhead
- More fragile (depends on DOM)

---

## Testing Your Implementation

### Unit Test Example

```python
def test_research_bbc_story():
    """Test research on a real BBC story."""
    researcher = PerplexityResearcher(config)
    
    # Create test story
    story = RawStory(
        title='Trump Resigns',
        description='US official steps down',
        url='https://...',
        date=datetime.now(),
        source='BBC',
        section='World News',
    )
    
    # Research it
    result = researcher.research(story)
    
    # Assertions
    assert len(result['corroboration']) >= 2, 'Should find 2+ sources'
    assert len(result['timeline']) > 0, 'Should have timeline'
    assert result['primary_source'] != 'Unknown', 'Should identify primary'
    
    print(result)
```

### Manual Testing

```bash
cd /home/r2d2/projects/news-engine

# Test import
python3 -c "from news_engine.research import PerplexityResearcher; print('✓ Import works')"

# Test with story
python3 << EOF
from news_engine.research import PerplexityResearcher
from news_engine.models import RawStory
from news_engine.config import get_default_config
from datetime import datetime

config = get_default_config()
researcher = PerplexityResearcher(config.perplexity)

story = RawStory(
    title='Trump Iran War',
    description='US military action',
    url='https://example.com',
    date=datetime.now(),
    source='BBC',
    section='World News',
)

result = researcher.research(story)
print(f'Sources: {len(result["corroboration"])}')
print(f'Timeline: {len(result["timeline"])}')
print(f'Contradictions: {len(result["contradictions"])}')
print(f'Primary: {result["primary_source"]}')
EOF
```

---

## Integration Checklist

- [ ] Import web_search correctly
- [ ] Handle empty results
- [ ] Extract corroboration (outlet names)
- [ ] Extract timeline (date, outlet, claim)
- [ ] Extract contradictions (conflicting claims)
- [ ] Identify primary source (who reported first)
- [ ] Return correct Dict structure
- [ ] Add error handling
- [ ] Add logging
- [ ] Type hints on all functions
- [ ] Test with real stories
- [ ] Commit with clear message

---

## Recommendation

**Use Option 1 (Perplexity):**
- Simpler
- Faster
- Less maintenance
- Works out of the box with web_search tool

**Switch to Option 2 (Playwright) only if:**
- You need full article text
- You need more granular control
- Basic search isn't enough

---

## Expected Output Example

```python
{
    'corroboration': ['BBC', 'Reuters', 'AP', 'CNN', 'Fox News'],
    'timeline': [
        {
            'date': '2026-03-16',
            'outlet': 'BBC',
            'claim': 'National Counterterrorism Center Director Joe Kent resigned'
        },
        {
            'date': '2026-03-16',
            'outlet': 'Reuters',
            'claim': 'Official calls for policy reversal on Iran war'
        },
        {
            'date': '2026-03-17',
            'outlet': 'Fox News',
            'claim': 'Administration responds to resignation'
        },
    ],
    'contradictions': [
        'Fox News claims Kent was fired vs Reuters says he resigned',
    ],
    'primary_source': 'BBC',
}
```

---

## Next: Once research.py is Done

1. ✅ Commit to git
2. ✅ Run full pipeline: `python3 main.py --dry-run --verbose`
3. ✅ Check parallel execution works
4. ✅ Generate first real edition
5. ✅ Report back to Suhail

---

**Start with Option 1 (Perplexity). It's simpler and should work great.**
