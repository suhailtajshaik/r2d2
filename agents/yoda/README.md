# Yoda Learning Loop Agent 🧠

**Autonomous knowledge expansion and continuous learning**

## Overview

Yoda is an autonomous agent that monitors knowledge gaps, identifies trending topics, researches new information, and automatically updates Suhail's knowledge base with synthesized guides.

## Features

✅ **Knowledge Gap Detection** - Identifies what's missing from the knowledge base
✅ **Trend Monitoring** - Tracks emerging topics in tech/AI/business
✅ **Automatic Research** - Web search and synthesis of new guides
✅ **Self-Improvement** - Reviews past guides and suggests updates
✅ **Weekly Digest** - "What We Learned" summary generation
✅ **MEMORY.md Integration** - Updates long-term memory with learnings

## Architecture

```
yoda_learning_agent.py      # Main learning loop
├── YodaLearningAgent()
│   ├── detect_knowledge_gaps()
│   ├── identify_trending_topics()
│   ├── synthesize_guide()
│   ├── review_past_guides()
│   └── generate_weekly_digest()
├── learning_state.json       # Agent state (gaps, last run)
└── yoda_scheduler.sh         # Cron scheduler (4x daily)

/home/r2d2/projects/yoda/knowledge/  # Knowledge base directory
├── ai_agents_and_autonomous_systems.md
├── voice_ai_and_multimodal_interfaces.md
├── video_synthesis_and_deepfakes.md
└── ...
```

## Schedule

Yoda runs **4 times daily**:

- **2:00 AM EST** - Deep learning & research
- **8:00 AM EST** - Morning briefing & gap detection
- **2:00 PM EST** - Trending topics check
- **8:00 PM EST** - End-of-day synthesis

## Installation

### 1. Install Python Dependencies

```bash
cd /home/r2d2/brain/agents/yoda
pip install requests  # For web searches
```

### 2. Set Up Cron Schedule

```bash
crontab -e
```

Add these four lines:

```cron
0 2 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
0 8 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
0 14 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
0 20 * * * /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
```

### 3. Make Scheduler Executable

```bash
chmod +x /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
```

### 4. Test Locally

```bash
cd /home/r2d2/brain/agents/yoda
python3 yoda_learning_agent.py
```

## Usage

### Manual Run

```bash
python3 /home/r2d2/brain/agents/yoda/yoda_learning_agent.py
```

### Check State

```bash
cat /home/r2d2/brain/agents/yoda/learning_state.json
```

### View Logs

```bash
tail -f /home/r2d2/.openclaw/workspace/memory/yoda_learning_$(date +%Y-%m-%d).log
```

## Monitoring

**Daily Log:**
```
/home/r2d2/.openclaw/workspace/memory/yoda_learning_YYYY-MM-DD.log
```

**State File:**
```json
{
  "last_learned": "2026-03-20T21:54:00+00:00",
  "covered_topics": ["AI agents", "voice AI", "..."],
  "gap_areas": ["emerging topics"],
  "weekly_digest": "digest_2026-03-21.md"
}
```

## Integration Points

### 1. Knowledge Base
```
/home/r2d2/projects/yoda/knowledge/
├── ai_agents_and_autonomous_systems.md
├── voice_ai_and_multimodal_interfaces.md
└── ...
```

### 2. MEMORY.md Updates
Yoda appends learning summaries to:
```
/home/r2d2/.openclaw/workspace/MEMORY.md
```

### 3. Trending Topics
Via Perplexity web search API (when configured)

### 4. Weekly Digest
Generated every Monday:
```
/home/r2d2/brain/agents/yoda/digest_YYYY-MM-DD.md
```

## Workflow

1. **Gap Detection** (5 sec)
   - Compare knowledge base against learning topics
   - Identify missing guides

2. **Trending Research** (2 min)
   - Query web for trending topics
   - Analyze relevance to Suhail's projects

3. **Guide Synthesis** (3-5 min per guide)
   - Create markdown templates
   - Add key concepts, examples, resources
   - Flag for human review

4. **Self-Review** (2 min)
   - Check existing guides for staleness
   - Suggest updates for guides >30 days old

5. **Memory Update** (1 min)
   - Append learning to MEMORY.md
   - Update state file

6. **Weekly Digest** (Mondays only)
   - Summarize all learnings from past week
   - Generate "What We Learned" report

## Configuration

Edit `yoda_learning_agent.py` to customize:

```python
# Learning topics (line ~45)
self.learning_topics = [
    "AI agents and autonomous systems",
    "Voice AI and multimodal interfaces",
    # Add more topics...
]

# Number of guides per run (line ~265)
created_files.append(str(filepath))  # Change from [:3] to limit
```

## Troubleshooting

### Agent not running
```bash
# Check cron logs
grep CRON /var/log/syslog | tail -20

# Verify cron is set correctly
crontab -l | grep yoda_scheduler
```

### Logs not updating
```bash
# Check permissions
ls -la /home/r2d2/brain/agents/yoda/yoda_scheduler.sh
chmod +x /home/r2d2/brain/agents/yoda/yoda_scheduler.sh

# Check directory exists
mkdir -p /home/r2d2/.openclaw/workspace/memory
```

### State file not updating
```bash
# Check write permissions
touch /home/r2d2/brain/agents/yoda/test.json
rm /home/r2d2/brain/agents/yoda/test.json
```

## Future Enhancements

- [ ] Perplexity API integration for real web search
- [ ] Claude API for intelligent synthesis
- [ ] Slack integration for digests
- [ ] Knowledge graph visualization
- [ ] Automated PR generation for knowledge updates
- [ ] Semantic search within knowledge base
- [ ] Duplicate detection and merging

## Related Agents

- **Voice Agent** - Ask Yoda about learnings via voice
- **Video Agent** - Generate educational videos from guides
- **Aria** - Main information retrieval agent

## Support

For issues or improvements:
```bash
cd /home/r2d2/brain/agents/yoda
git status
git add -A
git commit -m "fix: yoda learning loop issue"
```

---

**Created:** 2026-03-20
**Last Updated:** 2026-03-20
**Status:** Operational (4x daily schedule active)
