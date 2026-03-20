# Quick Start Guide

Get the Research Agent up and running in 5 minutes.

## Installation (One-time)

```bash
# Navigate to research agent directory
cd /home/r2d2/brain/agents/research

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python3 research.py --help
```

## Run a Sample Query

```bash
# Basic research on AI safety
python3 research.py \
  --topic "What's the latest in AI safety research?" \
  --keywords "alignment, AGI, safety" \
  --depth 2 \
  --format pretty
```

**Expected output:** JSON with:
- Topic and keywords
- 5-8 analyzed sources
- Key findings
- Credibility scores (0.0-1.0)
- Consensus analysis
- Any contradictions

## Common Use Cases

### 1. Quick Research (Fast)
```bash
python3 research.py --topic "Quantum computing" --depth 1
```
**Takes:** ~30-45 seconds  
**Sources:** 3-5

### 2. Standard Research (Balanced)
```bash
python3 research.py --topic "Climate change mitigation" --keywords "carbon, renewable" --depth 2
```
**Takes:** ~45-90 seconds  
**Sources:** 5-8

### 3. Deep Research (Thorough)
```bash
python3 research.py \
  --topic "Machine learning trends 2024" \
  --keywords "transformers, neural networks, LLM" \
  --depth 3 \
  --format pretty \
  --output ml_research.json
```
**Takes:** ~90-150 seconds  
**Sources:** 8-10  
**Output:** Saved to `ml_research.json`

### 4. Save Results
```bash
python3 research.py \
  --topic "Cryptocurrency market" \
  --output results.json
```

### 5. Verbose Mode (Debugging)
```bash
python3 research.py \
  --topic "Cloud computing" \
  --verbose
```

## Understanding the Output

### Key Fields

**Credibility Score (0.0-1.0)**
- 0.95: Nature, Science, ArXiv (academic)
- 0.85: News outlets (NYT, BBC)
- 0.75: Wikipedia
- 0.65: Medium, LinkedIn
- 0.55: Twitter, Reddit

**Confidence Levels**
- `high` - From high-credibility sources (>0.8)
- `medium` - From moderate sources (0.6-0.8)

**Severity (Contradictions)**
- `high` - Major conflicting claims
- `medium` - Minor disagreements

### Example Output

```json
{
  "topic": "AI safety research",
  "key_findings": [
    {
      "statement": "Recent focus on AI alignment...",
      "source_url": "https://example.com/article",
      "confidence": "high"
    }
  ],
  "sources": [
    {
      "domain": "nature.com",
      "credibility_score": 0.95,
      "relevance": 0.87
    }
  ],
  "consensus": "Strong consensus across high-credibility sources",
  "credibility_analysis": {
    "average_score": 0.82,
    "high_credibility_count": 4
  }
}
```

## Workflow Examples

### For Researchers
```bash
# Gather current state of field
python3 research.py \
  --topic "Recent advances in your field" \
  --depth 3 \
  --output field_overview.json

# Review findings and share
cat field_overview.json | python3 -m json.tool
```

### For Journalists
```bash
# Quick background research
python3 research.py \
  --topic "Current events topic" \
  --keywords "breaking news, latest" \
  --depth 2 \
  --format pretty
```

### For Decision Making
```bash
# Research before major decisions
python3 research.py \
  --topic "Technology you're evaluating" \
  --keywords "pros, cons, adoption" \
  --depth 3 \
  --output decision_research.json

# Check consensus for credibility
grep "consensus" decision_research.json
```

## Tips & Tricks

**Narrow Results with Keywords**
```bash
# Instead of broad search:
python3 research.py --topic "Machine learning"

# Use specific keywords:
python3 research.py \
  --topic "Machine learning" \
  --keywords "NLP, transformers, BERT"
```

**Increase Search Depth for Important Topics**
```bash
# Standard depth
python3 research.py --topic "..." --depth 2

# Deep research for critical decisions
python3 research.py --topic "..." --depth 3
```

**Chain with Other Tools**
```bash
# Save to JSON, then convert to PDF
python3 research.py --topic "..." --output result.json
# Convert using another tool or script
```

**Batch Research**
```bash
# Research multiple topics
for topic in "AI safety" "Quantum computing" "Climate tech"; do
  python3 research.py --topic "$topic" --depth 1 --output "${topic// /_}.json"
done
```

## Troubleshooting

### No results found
```bash
# Use simpler keywords
python3 research.py --topic "Your topic" --keywords "general, common"

# Increase depth
python3 research.py --topic "Your topic" --depth 3
```

### Want more sources
```bash
# Increase depth level (5-10 sources)
python3 research.py --topic "..." --depth 3
```

### Need detailed logging
```bash
# Enable verbose mode
python3 research.py --topic "..." --verbose

# Redirect to file for review
python3 research.py --topic "..." --verbose 2>&1 | tee debug.log
```

### Output validation
```bash
# Check JSON is valid
python3 research.py --topic "..." | python3 -m json.tool

# Pretty print JSON
python3 research.py --topic "..." --format pretty
```

## Next Steps

1. **Try different topics** - Test with your own research questions
2. **Adjust depth** - Find the right balance between speed and comprehensiveness
3. **Save results** - Use `--output` to save for later review
4. **Integrate** - Use output JSON with other tools (notebooks, databases, etc.)
5. **Extend** - See INTEGRATION.md for connecting with OpenClaw tools

## Performance Reference

| Depth | Sources | Time | Use Case |
|-------|---------|------|----------|
| 1 | 3-5 | 30-45s | Quick overview |
| 2 | 5-8 | 45-90s | Standard research |
| 3 | 8-10 | 90-150s | Deep analysis |

## Need Help?

```bash
# View help
python3 research.py --help

# Run tests
python3 test_research.py

# Read full documentation
cat README.md
```

---

**Happy researching! 🔍**
