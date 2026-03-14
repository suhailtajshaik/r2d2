---
name: last30days
description: Show activity summary from the last 30 days. Use when user asks for /last30days, recent activity, what happened recently, or wants a summary of past work and events.
---

# Last 30 Days Summary

Generate a summary of activities, decisions, and events from the last 30 days by reading daily memory files.

## Workflow

1. List all daily memory files from `memory/` directory
2. Filter to last 30 days (files named `YYYY-MM-DD.md`)
3. Read and summarize each file's key points
4. Present a consolidated summary organized by:
   - **Projects worked on** - What got built/fixed
   - **Key decisions** - Important choices made
   - **Events** - Meetings, trips, notable happenings
   - **Learnings** - Technical or personal insights

## Script Usage

Run the collector script to gather all entries:

```bash
bash skills/last30days/scripts/collect.sh
```

This outputs all daily entries from the last 30 days concatenated together.

## Output Format

Present the summary in a conversational, scannable format:

```
## 🗓️ Last 30 Days (DATE_RANGE)

### 📦 Projects
- Project A: Brief description of work done
- Project B: Brief description of work done

### 🎯 Key Decisions
- Decision about X
- Choice regarding Y

### 📅 Events
- Event 1
- Event 2

### 💡 Learnings
- Technical insight
- Process improvement
```

Keep it concise - this is a quick overview, not a detailed report.
