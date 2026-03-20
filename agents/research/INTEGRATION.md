# OpenClaw Integration Guide

This document describes how to integrate the Research Agent with OpenClaw tools.

## Overview

The Research Agent is designed to work with OpenClaw's `web_search` and `web_fetch` tools. The integration happens through wrapper modules that translate between OpenClaw's tool interface and the research agent's internal API.

## Architecture

```
Research Agent (research.py)
    ↓
research_functions.py (Core logic)
    ↓
Wrappers (web_search_wrapper.py, web_fetch_wrapper.py)
    ↓
OpenClaw Tools (web_search, web_fetch)
```

## Integration Steps

### 1. Enable Tool Integration in Wrappers

Edit `web_search_wrapper.py`:

```python
def search_perplexity(query: str, num_results: int = 8) -> List[Dict[str, Any]]:
    """Perform web search using Perplexity API."""
    
    # Uncomment for OpenClaw integration:
    from openclaw.tools import web_search
    
    results = web_search(query=query, count=min(num_results, 10))
    return parse_search_results(results)
```

Edit `web_fetch_wrapper.py`:

```python
def fetch_content(url: str, max_chars: int = 5000) -> Optional[str]:
    """Fetch and extract readable content from a URL."""
    
    # Uncomment for OpenClaw integration:
    from openclaw.tools import web_fetch
    
    content = web_fetch(url=url, extractMode='markdown', maxChars=max_chars)
    return content
```

### 2. Deploy as OpenClaw Subagent

From an OpenClaw agent session, spawn the research agent:

```python
import subprocess
import json

# Spawn research agent
result = subprocess.run([
    "python3",
    "/home/r2d2/brain/agents/research/research.py",
    "--topic", "AI safety research",
    "--keywords", "alignment, AGI",
    "--depth", "2"
], capture_output=True, text=True)

# Parse results
research_data = json.loads(result.stdout)
```

### 3. Use from OpenClaw CLI

```bash
# Direct invocation
python3 /home/r2d2/brain/agents/research/research.py \
  --topic "Your research question" \
  --depth 2

# With file output
python3 /home/r2d2/brain/agents/research/research.py \
  --topic "Your research question" \
  --output results.json
```

### 4. Integration with Other Skills

The Research Agent can be chained with other OpenClaw skills:

#### With GitHub Skill
```python
# Research code patterns, then commit findings
research_results = research_agent.query("GitHub Actions best practices")
github_skill.commit(research_results)
```

#### With Notion Skill
```python
# Add research findings to Notion database
research_data = research_agent.query("Latest ML techniques")
notion_skill.create_page(research_data)
```

#### With Send-Document Skill
```python
# Send research results as PDF
research_json = research_agent.query("Market analysis")
send_document(format_as_pdf(research_json))
```

## Tool Implementation Details

### web_search Integration

The `web_search` tool expects:
```python
web_search(
    query: str,              # Search query
    count: int = 5,         # Number of results (1-10)
    country: str = 'US',    # Country code
    freshness: str = None   # 'day', 'week', 'month', 'year'
)
```

Returns:
```python
[
    {
        'title': str,
        'url': str,
        'snippet': str,
        'source': str
    }
]
```

### web_fetch Integration

The `web_fetch` tool expects:
```python
web_fetch(
    url: str,
    extractMode: str = 'markdown',  # 'markdown' or 'text'
    maxChars: int = 5000
)
```

Returns:
```python
# Markdown or text content as string
```

## Running Tests with Tools

To test with actual OpenClaw tools:

1. Ensure OpenClaw is running:
```bash
openclaw gateway status
```

2. Update wrappers to enable tool imports

3. Run the test script:
```bash
cd /home/r2d2/brain/agents/research
python3 test_research.py
```

## Environment Variables

Set these in your environment for tool integration:

```bash
# OpenClaw connection
export OPENCLAW_HOST="localhost"
export OPENCLAW_PORT="8080"

# Perplexity API (if using direct API)
export PERPLEXITY_API_KEY="your_key_here"

# Logging
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

## Error Handling

The agent gracefully handles tool failures:

```python
try:
    results = web_search(query)
except ToolError as e:
    logger.error(f"Search failed: {e}")
    # Continue with cached/alternative results
```

### Common Issues

**Tool not found**
- Ensure OpenClaw gateway is running
- Check tool names match exactly (`web_search`, `web_fetch`)

**Content fetch timeout**
- Increase `max_chars` limit if needed
- Some sites may block automated requests

**Search returns no results**
- Try different keywords
- Adjust depth level
- Check network connectivity

## Performance Tuning

### Adjust Depth vs Speed

```bash
# Quick research (3-5 sources, ~30s)
--depth 1

# Balanced (5-8 sources, ~60s)
--depth 2

# Comprehensive (8-10 sources, ~120s)
--depth 3
```

### Batch Processing

For multiple research queries:

```bash
# Sequential (slower but less resource intensive)
for query in "${queries[@]}"; do
    python3 research.py --topic "$query" --depth 1
done

# Parallel (faster if resources available)
parallel python3 research.py --topic {} --depth 1 ::: "${queries[@]}"
```

## Monitoring

Enable verbose logging for debugging:

```bash
python3 research.py \
  --topic "..." \
  --verbose \
  2>&1 | tee research.log
```

Log levels:
- `DEBUG` - Detailed execution trace
- `INFO` - Normal operation
- `WARNING` - Non-critical issues
- `ERROR` - Failures

## Extending the Agent

### Add Custom Analysis

Create a new analysis module in `analysis/`:

```python
# analysis/sentiment_analysis.py

def analyze_sentiment(sources: List[Source]) -> Dict[str, Any]:
    """Analyze sentiment across sources."""
    # Implementation
    pass
```

Import in `research_functions.py`:
```python
from analysis.sentiment_analysis import analyze_sentiment

result.sentiment = analyze_sentiment(sources)
```

### Add Data Sources

Extend `web_search_wrapper.py` to support additional sources:

```python
def search_academic(query: str) -> List[Dict]:
    """Search academic papers."""
    from openclaw.tools import academic_search
    return academic_search(query)
```

## Deployment Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test basic functionality: `python3 test_research.py`
- [ ] Enable tool wrappers in `web_*_wrapper.py`
- [ ] Set environment variables
- [ ] Verify OpenClaw tools are available
- [ ] Run sample query: `python3 research.py --topic "test" --depth 1`
- [ ] Check output format and credibility scores
- [ ] Integrate with other agents/skills as needed

## Support

For issues or enhancements:

1. Check logs: `python3 research.py --verbose`
2. Verify tool availability: `which web_search` (if CLI tool)
3. Test wrappers independently:
   ```python
   from web_search_wrapper import search_perplexity
   results = search_perplexity("test query")
   ```

## API Reference

### Main Function

```python
def perform_research(
    topic: str,           # Research topic
    keywords: str = '',   # Comma-separated keywords
    depth: int = 2,       # 1-3, research depth
    verbose: bool = False # Enable logging
) -> ResearchResult
```

### Result Object

```python
@dataclass
class ResearchResult:
    topic: str
    keywords: List[str]
    timestamp: str
    depth: int
    key_findings: List[Dict]
    sources: List[Dict]
    credibility_analysis: Dict
    consensus: str
    contradictions: List[Dict]
    metadata: Dict
```

### Source Object

```python
@dataclass
class Source:
    title: str
    url: str
    domain: str
    content: Optional[str]
    credibility_score: float
    publication_date: Optional[str]
    relevance: float
```

---

**Last Updated:** 2024-03-18
**Version:** 1.0.0
