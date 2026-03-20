# 🔍 Research Agent - START HERE

Welcome to the Research Agent! This document will get you up and running in minutes.

## What is the Research Agent?

An autonomous research tool that:
- 🔎 Searches the web using Perplexity API
- 📄 Extracts full article content
- ⭐ Scores source credibility (0.0-1.0)
- 💡 Identifies key findings
- 🤝 Detects consensus and contradictions
- 📋 Returns structured JSON output

Perfect for quick research, background checks, or comprehensive analysis.

## 5-Minute Setup

```bash
# 1. Navigate to the directory
cd /home/r2d2/brain/agents/research

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test it works
python3 research.py --topic "AI safety" --depth 1
```

**That's it!** You now have a working research agent.

## Common Commands

### Quick Research (30 seconds)
```bash
python3 research.py --topic "Your question" --depth 1
```

### Standard Research (1 minute)
```bash
python3 research.py \
  --topic "Your question" \
  --keywords "key1, key2" \
  --depth 2
```

### Save to File
```bash
python3 research.py \
  --topic "Your question" \
  --depth 2 \
  --output results.json
```

### Pretty-Printed JSON
```bash
python3 research.py \
  --topic "Your question" \
  --format pretty
```

### Debug Mode
```bash
python3 research.py \
  --topic "Your question" \
  --verbose
```

## What You Get

Example output for research on "AI safety":

```json
{
  "topic": "What's the latest in AI safety research?",
  "key_findings": [
    {
      "statement": "Research increasingly focuses on scalable oversight mechanisms...",
      "source_url": "https://arxiv.org/...",
      "confidence": "high"
    }
  ],
  "sources": [
    {
      "domain": "arxiv.org",
      "credibility_score": 0.92,
      "relevance": 0.95
    }
  ],
  "consensus": "Strong consensus across high-credibility sources",
  "contradictions": []
}
```

See `SAMPLE_OUTPUT.json` for a complete example.

## Understanding Credibility Scores

Sources are scored 0.0-1.0 based on domain reputation:

| Score | Type | Examples |
|-------|------|----------|
| 0.90-0.95 | Academic | arxiv.org, nature.com, ieee.org |
| 0.85 | News/Professional | nytimes.com, bbc.com |
| 0.75 | Reference | wikipedia.org |
| 0.65 | Blog/Social | medium.com, linkedin.com |
| 0.55-0.60 | User-Generated | twitter.com, reddit.com |

**Higher score = More trustworthy source**

## Research Depth Levels

| Level | Sources | Time | Best For |
|-------|---------|------|----------|
| 1 | 3-5 | 30-45s | Quick overview |
| 2 | 5-8 | 45-90s | Standard research |
| 3 | 8-10 | 90-150s | Deep analysis |

Use `--depth 1` for speed, `--depth 3` for thoroughness.

## Key Features

✅ **Structured Output** - JSON format for easy integration  
✅ **Source Credibility** - Automatic reputation scoring  
✅ **Finding Extraction** - Top 5 key statements per research  
✅ **Consensus Detection** - Identifies agreement level  
✅ **Contradiction Finding** - Flags conflicting claims  
✅ **Keyword Filtering** - Focus research on specific terms  
✅ **Verbose Logging** - Debug with `--verbose` flag  
✅ **File Output** - Save results with `--output`

## Documentation

**New to the tool?**
→ Read `QUICKSTART.md` (5 minutes)

**Want full details?**
→ Read `README.md` (complete reference)

**Setting up with OpenClaw?**
→ Read `INTEGRATION.md` (tool integration)

**Need project overview?**
→ Read `MANIFEST.md` (architecture)

## Real-World Examples

### Example 1: Quick Background Research
```bash
python3 research.py --topic "Latest developments in quantum computing"
# Output: Quick overview in 30-45 seconds
```

### Example 2: News Story Research
```bash
python3 research.py \
  --topic "Major events in tech industry 2024" \
  --keywords "disruption, innovation" \
  --depth 2
# Output: Balanced view from high-credibility sources
```

### Example 3: Decision-Making Research
```bash
python3 research.py \
  --topic "Should we adopt Technology X?" \
  --keywords "pros, cons, adoption rate" \
  --depth 3 \
  --output decision_research.json

# Output: Comprehensive analysis saved to file
cat decision_research.json | python3 -m json.tool
```

### Example 4: Integration with Other Tools
```python
import subprocess, json

# Run research agent
result = subprocess.run(
    ["python3", "research.py",
     "--topic", "Your question",
     "--depth", "2"],
    capture_output=True,
    text=True
)

# Parse and use results
data = json.loads(result.stdout)
consensus = data['consensus']
sources = data['sources']
print(f"Consensus: {consensus}")
print(f"Sources: {len(sources)} analyzed")
```

## Troubleshooting

**Getting no results?**
```bash
# Try simpler keywords
python3 research.py --topic "Your topic" --keywords "general"

# Or increase depth
python3 research.py --topic "Your topic" --depth 3
```

**Want more details?**
```bash
# Use verbose mode
python3 research.py --topic "..." --verbose

# Or increase depth
python3 research.py --topic "..." --depth 3
```

**Need to debug?**
```bash
# Run with full logging
python3 research.py --topic "..." --verbose 2>&1 | tee debug.log

# Check output is valid JSON
python3 research.py --topic "..." | python3 -m json.tool
```

## Performance Tips

1. **Use keywords** - Narrows results, faster processing
2. **Match depth to need** - Depth 1 for speed, 3 for comprehensiveness
3. **Batch research** - Run multiple queries in sequence
4. **Save results** - Use `--output` to avoid re-running queries

## What's Next?

1. **Try a query** - `python3 research.py --topic "something" --depth 1`
2. **Review output** - Check `SAMPLE_OUTPUT.json` to understand structure
3. **Explore options** - Run `python3 research.py --help`
4. **Integrate** - See `INTEGRATION.md` to connect with OpenClaw tools
5. **Automate** - Use in scripts or batch workflows

## Need Help?

```bash
# View all options
python3 research.py --help

# Run tests
python3 test_research.py

# Read documentation
cat README.md        # Full reference
cat QUICKSTART.md    # Quick start guide
cat INTEGRATION.md   # OpenClaw setup
cat MANIFEST.md      # Architecture overview
```

## Project Stats

📦 **Size:** 100 KB  
📄 **Files:** 12 (code, docs, tests, samples)  
🐍 **Language:** Python 3.7+  
📚 **Dependencies:** Minimal (requests, dateutil)  
⚡ **Speed:** 30-150 seconds depending on depth  
💾 **Memory:** 50-100 MB  

## Key Concepts

### Credibility Scoring
Sources automatically scored based on:
- **Domain reputation** - Academic > News > Blog > Social
- **Content quality** - Longer content, citations = higher score
- **Range:** 0.0 (unreliable) to 1.0 (highly trustworthy)

### Consensus
The agent detects if sources agree:
- **Strong consensus** - >80% high-credibility agreement
- **Moderate consensus** - 60-80% agreement
- **Weak consensus** - <60% agreement or low-credibility sources

### Contradictions
Automatically flagged when sources make conflicting claims:
- **Severity: high** - Major disagreements on core facts
- **Severity: medium** - Minor variations in approach/opinion

## Examples of What It Can Research

- Latest research trends in any field
- Current news and events
- Technology/product comparisons
- Industry analysis and insights
- Best practices and standards
- Historical timelines
- Market analysis
- Scientific findings
- Business intelligence
- And much more!

## One Last Thing

**The research agent returns data, not opinions.** It finds multiple sources, scores them for credibility, and returns what it finds. You interpret the results.

Always:
- ✅ Read primary sources for important decisions
- ✅ Check publication dates (recency matters)
- ✅ Verify high-stakes information independently
- ✅ Consider credibility scores, not just quantity of sources

---

## Quick Reference Card

```bash
# Basic
python3 research.py --topic "Your question"

# With keywords
python3 research.py --topic "Q" --keywords "k1, k2"

# Deep research
python3 research.py --topic "Q" --depth 3

# Save to file
python3 research.py --topic "Q" --output results.json

# Pretty print
python3 research.py --topic "Q" --format pretty

# Debug
python3 research.py --topic "Q" --verbose

# Help
python3 research.py --help

# Test
python3 test_research.py
```

---

**Ready to research?** Start with:
```bash
python3 research.py --topic "Your question" --depth 2
```

**Questions?** Check the relevant doc:
- QUICKSTART.md - Getting started
- README.md - Full documentation
- INTEGRATION.md - OpenClaw setup
- SAMPLE_OUTPUT.json - Example output

Happy researching! 🚀
