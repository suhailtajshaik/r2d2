# Research Agent

A standalone Python agent for autonomous research queries with structured analysis and credibility evaluation.

## Overview

The Research Agent performs systematic research on any topic by:

1. **Web Search** - Searches for relevant sources using Perplexity API
2. **Content Fetching** - Extracts full article content from top results
3. **Source Analysis** - Evaluates credibility based on domain reputation and content quality
4. **Finding Extraction** - Identifies key claims and statements
5. **Consensus Analysis** - Detects agreement and contradictions across sources
6. **Structured Output** - Returns JSON with findings, sources, and metadata

## Features

- 📊 **Credibility Scoring** - Rates sources (0.0-1.0) based on domain reputation and content quality
- 🔍 **Keyword Filtering** - Focuses research on specific terms
- ⚖️ **Contradiction Detection** - Identifies conflicting claims across sources
- 📈 **Consensus Analysis** - Determines level of agreement
- 🎯 **Depth Levels** - Adjustable search depth (brief, standard, deep)
- 📋 **Structured Output** - JSON format with sources, findings, and metadata
- 🔄 **Async Ready** - Can be spawned as OpenClaw subagent

## Installation

```bash
# Clone or extract the research agent
cd /home/r2d2/brain/agents/research

# Install dependencies
pip install -r requirements.txt

# Make script executable
chmod +x research.py
```

## Usage

### Basic Usage

```bash
python3 research.py --topic "AI safety" --keywords "alignment, AGI" --depth 2
```

### Command Line Options

```
--topic TEXT              Research topic/question (required)
--keywords TEXT           Comma-separated keywords (optional)
--depth {1,2,3}          Research depth level (default: 2)
                         1 = brief (3-5 sources)
                         2 = standard (5-8 sources)
                         3 = deep (8-10 sources)
--output FILE            Save output to JSON file (default: stdout)
--format {json,pretty}   Output format (default: json)
--verbose                Enable verbose logging
```

### Examples

**Basic research:**
```bash
python3 research.py --topic "Quantum computing trends"
```

**With keywords:**
```bash
python3 research.py --topic "Climate change" --keywords "carbon, emissions, mitigation" --depth 3
```

**Save to file:**
```bash
python3 research.py --topic "Cryptocurrency" --output research_results.json
```

**Pretty-printed output:**
```bash
python3 research.py --topic "Machine learning" --format pretty --verbose
```

## Output Format

The agent returns structured JSON with the following schema:

```json
{
  "topic": "AI safety",
  "keywords": ["alignment", "AGI"],
  "timestamp": "2024-03-18T14:53:00Z",
  "depth": 2,
  "key_findings": [
    {
      "statement": "Key finding text...",
      "source_url": "https://...",
      "confidence": "high"
    }
  ],
  "sources": [
    {
      "title": "Article title",
      "url": "https://...",
      "domain": "example.com",
      "credibility_score": 0.92,
      "publication_date": "2024-03-15",
      "relevance": 0.85,
      "content_preview": "First 200 characters of content..."
    }
  ],
  "credibility_analysis": {
    "average_score": 0.82,
    "highest_score": 0.95,
    "lowest_score": 0.65,
    "high_credibility_count": 4,
    "medium_credibility_count": 2,
    "low_credibility_count": 1
  },
  "consensus": "Strong consensus across high-credibility sources",
  "contradictions": [
    {
      "claim_1": "First claim...",
      "source_1": "https://...",
      "claim_2": "Conflicting claim...",
      "source_2": "https://...",
      "severity": "medium"
    }
  ],
  "metadata": {
    "total_sources_found": 8,
    "sources_analyzed": 5,
    "research_duration_note": "See timestamp for research time"
  }
}
```

## Architecture

### Core Modules

- **`research.py`** - CLI entry point and argument parsing
- **`research_functions.py`** - Core research logic and analysis
- **`web_search_wrapper.py`** - Perplexity API integration
- **`web_fetch_wrapper.py`** - Content fetching integration

### Key Classes

#### `Source`
Represents a research source with credibility and relevance scores.

```python
Source(
    title: str,
    url: str,
    domain: str,
    content: Optional[str],
    credibility_score: float,
    publication_date: Optional[str],
    relevance: float
)
```

#### `ResearchResult`
Structured research output with findings and analysis.

```python
ResearchResult(
    topic: str,
    keywords: List[str],
    timestamp: str,
    depth: int,
    key_findings: List[Dict],
    sources: List[Dict],
    credibility_analysis: Dict,
    consensus: str,
    contradictions: List[Dict],
    metadata: Dict
)
```

## Credibility Scoring

Sources are scored 0.0-1.0 based on:

### Domain Reputation (Primary)
- Academic/Scientific: `nature.com`, `arxiv.org`, `ieee.org` → 0.90-0.95
- News/Journalism: `nytimes.com`, `bbc.com`, `economist.com` → 0.85
- Tech: `github.com`, `stackoverflow.com` → 0.85
- Reference: `wikipedia.org` → 0.75
- Blog/Social: `medium.com`, `linkedin.com`, `twitter.com` → 0.55-0.65
- User-Generated: `reddit.com`, `youtube.com` → 0.55-0.60

### Content Quality (Modifier)
- +0.10 for content >1000 characters
- +0.05 for citations/references
- Capped at 1.0

## OpenClaw Integration

To deploy as an OpenClaw subagent:

```bash
# Spawn the research agent from another OpenClaw agent
sessions_spawn --name research --runtime openclaw \
  --command "python3 /home/r2d2/brain/agents/research/research.py --topic 'your query' --depth 2"
```

Or invoke directly in Python:

```python
import subprocess
import json

result = subprocess.run(
    ["python3", "/home/r2d2/brain/agents/research/research.py",
     "--topic", "AI safety",
     "--keywords", "alignment",
     "--depth", "2"],
    capture_output=True,
    text=True
)

research_json = json.loads(result.stdout)
```

## Testing

Test with the sample query:

```bash
python3 research.py \
  --topic "What's the latest in AI safety research?" \
  --keywords "alignment, AGI, safety" \
  --depth 3 \
  --format pretty
```

Expected output will include:
- Recent AI safety research findings
- Source credibility analysis
- Consensus on key topics
- Any contradictions in approach

## Performance

### Typical Runtimes (varies with network)
- **Depth 1** (5 sources): ~30-45 seconds
- **Depth 2** (8 sources): ~45-90 seconds
- **Depth 3** (10 sources): ~90-150 seconds

### Resource Usage
- Memory: ~50-100 MB
- Network: 2-10 MB depending on content size
- CPU: Minimal (mostly I/O bound)

## Error Handling

The agent handles:
- Network errors (logs and continues)
- Invalid URLs (skipped in fetch)
- Missing content (marked in output)
- Empty search results (raises ValueError)

Enable verbose mode to see all errors:

```bash
python3 research.py --topic "..." --verbose
```

## Future Enhancements

- [ ] PDF/Document source support
- [ ] Academic paper indexing (Semantic Scholar, CrossRef)
- [ ] Image/chart extraction
- [ ] Multi-language support
- [ ] Citation graph analysis
- [ ] Source opinion detection (bias analysis)
- [ ] Timeline generation for historical topics
- [ ] Database caching of research results

## Dependencies

- **Python 3.7+**
- `requests` - HTTP requests
- `python-dateutil` - Date parsing
- **OpenClaw tools** - `web_search`, `web_fetch` (when deployed)

## License

Same as parent project (OpenClaw)

## Notes

- Designed as a standalone script—no dependencies on external frameworks
- Tool integration happens via wrapper modules for flexibility
- Can be extended with custom analysis functions
- Output JSON is standardized for easy integration with other tools
- Credibility scoring is heuristic-based; consider verification for critical decisions
