# Automated Learning System
**Status:** ✅ LIVE (2026-03-29)
**Purpose:** Continuous institutional learning from mistakes and patterns

---

## System Overview

```
R2D2 Experience          Lesson Creation           Auto-Sync              Yoda Integration
─────────────────      ────────────────────      ──────────            ─────────────────
  Mistake              Document lesson            Every 30 min          Reads new patterns
    ↓                  in lessons/ dir                 ↓                      ↓
  Root cause           • Technical patterns      lesson-sync-yoda.py    Behavioral guidance
    ↓                  • Behavioral patterns          ↓                      ↓
  Learn from it        • Prevention rules        Copies to Yoda/        Applies to future
    ↓                      ↓                      knowledge/ dir        interactions
  Write lesson         git commit                    ↓                      ↓
    ↓                      ↓                    Yoda learns new        Other agents learn
  git add              brain repo updated        patterns                  ↓
                                                     ↓                   Never repeat
                                            Daily report (9 AM)       Same mistake
```

---

## Components

### 1. Lesson Storage
**Location:** `/home/r2d2/brain/lessons/`
**Format:** Markdown files (one per incident/pattern)
**Content:**
- What went wrong (mistake description)
- Why it went wrong (root cause)
- How to fix it (correct approach)
- Prevention rules (decision frameworks)
- Applied to: Future interactions

**Current Lessons:**
- `nginx-spa-deployment.md` — SPA reverse proxy path rewriting
- `suhail-communication-patterns.md` — Intent recognition from user signals
- `api-architecture-mistake.md` — API key exposure in frontend code

### 2. Automated Sync Script
**Script:** `/home/r2d2/tools/lesson-sync-yoda.py`
**Triggers:** Every 30 minutes (cron: r2d2:lesson-sync-yoda)
**What it does:**
1. Scans `/home/r2d2/brain/lessons/` for new/updated `.md` files
2. Compares file hash against sync log
3. If new/changed: copies to `/home/r2d2/projects/yoda/knowledge/yoda-lesson-*.md`
4. Adds sync metadata (timestamp, source file)
5. Logs to sync state file

**Output Format:**
```
✅ Synced NEW lesson: nginx-spa-deployment.md → yoda-lesson-nginx-spa-deployment.md
🔄 Updated lesson: suhail-communication-patterns.md
📊 Summary: 2 new, 1 updated, 3 total synced
```

### 3. Daily Report Script
**Script:** `/home/r2d2/tools/lesson-report.py`
**Triggers:** 9 AM EST daily (cron: r2d2:daily-lesson-report)
**What it does:**
1. Reads sync state from lesson-sync-yoda.py
2. Generates human-readable summary
3. Lists all lessons by category
4. Reports Yoda integration status
5. Outputs to console (visible to Suhail via cron)

**Sample Output:**
```
📚 Daily Lesson Report — 2026-03-29 12:28 EDT

Summary:
- Total lessons: 3
- Last sync: 2026-03-29T12:28:25
- Yoda integration: ✅

Lessons Synced:
  • nginx-spa-deployment
  • suhail-communication-patterns
  • api-architecture-mistake

Categories: Technical (2), Behavioral (1)
```

### 4. Heartbeat Integration
**Location:** `/home/r2d2/.openclaw/workspace/HEARTBEAT.md`
**Rule:** On every heartbeat (~every 30 min), check for new lessons
**Action:** If new lessons exist in `/home/r2d2/brain/lessons/`, they'll be synced to Yoda

---

## Workflow: Turning Mistakes into Patterns

### Step 1: Experience & Document
```bash
# When something goes wrong:
1. Stop and analyze what happened
2. Identify the root cause
3. Document in /home/r2d2/brain/lessons/TOPIC.md
4. Include:
   - What I did wrong
   - Why it was wrong
   - Correct approach
   - Prevention rules
   - Links to related files
```

**Example File:**
```markdown
# Lesson: Nginx SPA Deployment
Date: 2026-03-29
Context: Prompt Studio blank page
Status: MISTAKE MADE → FIXED AND DOCUMENTED

The Mistake: Changed app code when infrastructure needed fixing
Root cause: Didn't recognize path rewriting pattern

The Solution: [detailed explanation]
Prevention Rule: When user says "fix infrastructure", don't change code
```

### Step 2: Automatic Sync
```
Lesson created → Saved to lessons/ → Git commit
                    ↓
            Every 30 minutes:
            lesson-sync-yoda.py runs
            Detects new file
            Copies to yoda/knowledge/
            Updates sync log
```

### Step 3: Yoda Integration
Yoda reads the new lesson file and:
- ✅ Adds patterns to behavioral models
- ✅ Updates decision trees
- ✅ Coaches R2D2 on same mistakes
- ✅ Shares patterns with other agents
- ✅ Prevents repeated failures

### Step 4: Daily Visibility
```
9 AM EST Daily:
lesson-report.py generates summary
Reports: lessons synced, categories, status
Visible to Suhail as daily reminder
```

---

## Prevention Framework

When a lesson is created, it includes:

### Decision Rules
```
IF situation X occurs
THEN do Y (not Z)
REASON: prevents mistake Z
```

### Escalation Signals
```
IF user says "A" twice in different ways
THEN I'm on wrong track
ACTION: Change approach fundamentally
```

### Layer Identification
```
IF code changes, think: Is this code or infrastructure?
IF vague feedback, ask clarifying questions
IF repeated feedback, stop iterating
```

---

## Cron Jobs (Automation)

| Job | Schedule | Script | Purpose |
|-----|----------|--------|---------|
| r2d2:lesson-sync-yoda | Every 30 min | lesson-sync-yoda.py | Sync lessons to Yoda |
| r2d2:daily-lesson-report | 9 AM EST daily | lesson-report.py | Daily summary |
| yoda:auto-learn | 2,8,14,20 EST | (Yoda) | Yoda knowledge updates |
| guardian:newspaper-monitor | Every 5 min | (Guardian) | Infrastructure monitoring |

---

## Integration with Yoda

### How Yoda Uses This System

1. **On startup:** Reads all files in `yoda/knowledge/yoda-lesson-*.md`
2. **In responses:** References lessons when advising R2D2
3. **In coaching:** "This looks like the nginx SPA pattern — remember lesson X"
4. **In prevention:** "Before you change code, identify the layer first"
5. **In new projects:** "I learned from SPA deployment — here's what works"

### Yoda Knowledge Files Created
```
/home/r2d2/projects/yoda/knowledge/
├── yoda-lesson-nginx-spa-deployment.md
├── yoda-lesson-suhail-communication-patterns.md
└── yoda-lesson-api-architecture-mistake.md
```

Each file includes:
- Original lesson content
- [Synced from R2D2 Learning] header
- Category metadata
- Integration notes

---

## Success Metrics

### For Technical Learning
- ✅ No repeated nginx SPA issues
- ✅ Correct layer identification on first try
- ✅ Single fix instead of multiple attempts

### For Behavioral Learning
- ✅ Recognize user intent immediately
- ✅ Honor veto signals ("don't change code")
- ✅ Respond to directional feedback
- ✅ Learn from escalation patterns

### For System Learning
- ✅ Daily reports show growing lesson library
- ✅ Yoda integration verified
- ✅ Patterns shared with other agents
- ✅ Zero repeated failures in documented areas

---

## Example: How It Works in Practice

### Incident: Prompt Studio Blank Page

**Stage 1: Mistake**
```
→ Changed Vite config (wrong)
→ Didn't recognize nginx needed rewrite rule (wrong)
→ Multiple Docker rebuilds (inefficient)
```

**Stage 2: Learning**
```
→ Root cause: Path rewriting pattern for reverse-proxied SPAs
→ Veto signal: "I don't think code changes are necessary"
→ Intent: Fix infrastructure, not code
```

**Stage 3: Documentation**
```
Created: /home/r2d2/brain/lessons/nginx-spa-deployment.md
Content: Technical pattern + behavioral pattern + prevention rules
```

**Stage 4: Automation**
```
Committed → lesson-sync-yoda.py runs (every 30 min)
→ Copied to yoda/knowledge/yoda-lesson-nginx-spa-deployment.md
→ Yoda reads and integrates
→ Daily report: "1 lesson synced"
```

**Stage 5: Prevention**
```
Future SPA deployment:
Yoda says: "Remember nginx path rewriting pattern"
R2D2 remembers: "Don't change code when user says fix infrastructure"
Result: ✅ Correct on first attempt
```

---

## Files & Locations

```
/home/r2d2/brain/
├── lessons/                           # Lesson repository
│   ├── nginx-spa-deployment.md
│   ├── suhail-communication-patterns.md
│   └── api-architecture-mistake.md
├── LEARNING_SYSTEM.md                 # This file
└── ... (other brain files)

/home/r2d2/tools/
├── lesson-sync-yoda.py               # Sync script (executable)
├── lesson-report.py                  # Report script
└── .lesson-sync-log.json             # Sync state (auto-created)

/home/r2d2/projects/yoda/knowledge/
├── yoda-lesson-nginx-spa-deployment.md
├── yoda-lesson-suhail-communication-patterns.md
└── yoda-lesson-api-architecture-mistake.md

/home/r2d2/.openclaw/workspace/
├── HEARTBEAT.md                       # Updated with lesson sync
├── MEMORY.md                          # User intent patterns
└── ... (other workspace files)
```

---

## How to Create New Lessons

### Quick Start
```bash
# 1. Create lesson file
nano /home/r2d2/brain/lessons/TOPIC-NAME.md

# 2. Write the lesson with sections:
#    - What went wrong
#    - Why it went wrong
#    - Correct approach
#    - Prevention rules
#    - Applied to: [context]

# 3. Git commit
cd /home/r2d2/brain
git add lessons/TOPIC-NAME.md
git commit -m "Lesson: TOPIC NAME (incident date)"

# 4. Automation handles the rest
#    (lesson-sync-yoda.py runs every 30 min)
```

### Lesson Template
```markdown
# Lesson: [Topic]
**Date:** [Date]
**Context:** [Incident description]
**Status:** ❌ MISTAKE MADE → ✅ FIXED AND DOCUMENTED

---

## The Mistake
[What I did wrong]

## Root Cause
[Why it happened]

## The Solution
[Correct approach]

## Decision Rules (Prevention)
```
IF [situation]
THEN [correct action]
REASON: [prevents what]
```

## Applied To
[Future interactions where this matters]

## References
[Links to related files, code, etc.]
```

---

## Monitoring & Health

### Check Sync Status
```bash
python3 /home/r2d2/tools/lesson-sync-yoda.py
# Output shows: new lessons, updated lessons, total synced

# Or check the log:
cat /home/r2d2/tools/.lesson-sync-log.json
```

### Check Cron Status
```bash
cron list | grep lesson
# Shows: r2d2:lesson-sync-yoda, r2d2:daily-lesson-report
```

### Verify Yoda Integration
```bash
ls /home/r2d2/projects/yoda/knowledge/yoda-lesson-*.md
# Should match lessons in /home/r2d2/brain/lessons/
```

---

## Future Enhancements

- [ ] Lesson search and discovery by topic
- [ ] Automated lesson summarization
- [ ] Pattern matching across lessons
- [ ] Similarity detection (find related lessons)
- [ ] Integration with Notion session log
- [ ] Lesson effectiveness tracking (did this prevent future mistakes?)
- [ ] Cross-agent lesson sharing

---

## Key Principle

**Learning is not a one-time event. Learning is a system.**

A mistake → lesson → sync → Yoda reads → prevents future → shared knowledge

This ensures:
- ✅ We never make the same mistake twice
- ✅ Knowledge is institutionalized, not forgotten
- ✅ Other agents benefit from our learning
- ✅ Continuous improvement is automatic
- ✅ No mental notes needed — it's all tracked

---

*Last updated: 2026-03-29*
*System live and operational*
