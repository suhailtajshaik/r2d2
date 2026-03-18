# 3PO Code Review Task — News Engine Hardening

**Source:** Yoda's Code Review (`/home/r2d2/brain/code-reviews/news-engine-review.md`)

**Priority:** CRITICAL → HIGH → MEDIUM

**Timeline:** Address CRITICAL before testing, then work through HIGH

---

## CRITICAL (Must Fix Before Production)

### 1. Implement research.py (Web Search Integration)
**Status:** Currently a STUB
**What:** research.py needs real web search integration

**Primary Method: Perplexity (web_search tool)**
```python
from web_search import web_search

# Search for story corroboration
results = web_search(
    query=f"{story.headline} {story.date.year}",
    count=10,
    freshness="week"
)
# Returns: [{outlet, published_date, description, url}, ...]
```

**Alternative: Playwright + Chrome Browser**
- Use if you need advanced scraping
- Can extract full article text, metadata, etc.
- More control than web_search

**Implementation Steps:**
1. Search web for story headline + key facts
2. Parse results to extract:
   - **corroboration**: list of outlet names [BBC, Reuters, AP, ...]
   - **timeline**: list of {date, outlet, claim} for story evolution
   - **contradictions**: list of conflicting claims between sources
   - **primary_source**: which outlet broke the story first
3. Return: Dict with {corroboration, timeline, contradictions, primary_source}

**File:** `/home/r2d2/projects/news-engine/news_engine/research.py`
**Lines:** Entire file (currently stub)

**Detailed Implementation Guide:** `/home/r2d2/brain/agents/3PO/research-py-implementation.md`

**Two Options:**
1. **Perplexity (Recommended)** — Use `web_search` tool
   - Simpler, faster, less maintenance
   - Works with existing tool
   
2. **Playwright + Chrome** — Advanced scraping
   - More control, full article text
   - Only if basic search isn't enough

**Acceptance Criteria:**
- [ ] web_search returns 3+ sources for real story
- [ ] timeline extraction works (dates tracked)
- [ ] contradiction detection works (conflicting claims identified)
- [ ] primary source identified correctly (who reported first)
- [ ] Handles edge cases (story not found, single source, etc.)
- [ ] Returns correct Dict: {corroboration, timeline, contradictions, primary_source}

---

### 2. Fix SSL Verification in feeds.py
**Status:** DANGEROUS in production
**Issue:** Line 34 has `verify_mode = ssl.CERT_NONE` (MITM vulnerability)
**Fix:**
- Option A: Remove SSL bypass (use proper certificates)
- Option B: Make it configurable (config.yaml switch)
- Option C: Add warning comment + only use in dev

**File:** `/home/r2d2/projects/news-engine/news_engine/feeds.py`
**Lines:** 31-34

**Recommendation:** Option A for production, but document requirement

---

### 3. Add Type Hints to All Functions
**Status:** Missing
**What:** Add type hints to function signatures
**Priority Modules:**
1. orchestrator.py (main pipeline)
2. factchecker.py (fact-checking)
3. intent_extractor.py (intent analysis)
4. analyzer.py (synthesis)

**Example Fix:**
```python
# BEFORE
def verify(self, story, research):

# AFTER
def verify(self, story: RawStory, research: Dict) -> FactCheck:
```

**Acceptance Criteria:**
- [ ] All public methods have return types
- [ ] All parameters have types (except self)
- [ ] `from typing import ...` imports added
- [ ] mypy passes (if available)

---

### 4. Add Input Validation to models.py
**Status:** No validation
**What:** Add __post_init__ checks to dataclasses

**File:** `/home/r2d2/projects/news-engine/news_engine/models.py`

**Fields to Validate:**
- FactCheck.overall_confidence: must be 0-100
- FactCheck.source_credibility: must be 0-100
- Verification.confidence: must be 0-100
- Claim.confidence: must be 0-100

**Example Fix:**
```python
@dataclass
class FactCheck:
    ...
    def __post_init__(self):
        assert 0 <= self.overall_confidence <= 100
        assert 0 <= self.source_credibility <= 100
```

**Acceptance Criteria:**
- [ ] All confidence scores validated (0-100)
- [ ] Validation raises AssertionError on invalid input
- [ ] Tests pass with valid data

---

## HIGH (Before Major Release)

### 5. Move Hardcoded Values to Config
**Status:** Scattered throughout code
**What:** Collect all magic numbers and move to config.yaml

**Hardcoded Values:**
1. orchestrator.py, line 88: `max_workers=4`
2. factchecker.py, lines 83-89: source credibility scores
3. factchecker.py, lines 60-72: claim verification confidence numbers
4. intent_extractor.py, lines 63-81: keyword lists
5. analyzer.py, lines 97-116: signal weights

**File to Update:** `/home/r2d2/projects/news-engine/config.yaml`

**Example Addition:**
```yaml
factchecker:
  source_credibility:
    high: [BBC, Reuters, AP, AFP]
    medium: [CNN, NDTV, TOI]
  confidence_scores:
    verified_3_sources: 95
    verified_2_sources: 85
    ...
```

**Acceptance Criteria:**
- [ ] All magic numbers in config.yaml
- [ ] Code reads from config instead
- [ ] Config is validated on load
- [ ] Can change values without code change

---

### 6. Improve Error Handling
**Status:** Too broad (catches `Exception`)
**What:** Catch specific exceptions

**File:** `/home/r2d2/projects/news-engine/news_engine/orchestrator.py`
**Lines:** 104, 111

**Current:**
```python
except Exception as e:
    logger.warning(...)
```

**Should Be:**
```python
except (TimeoutError, ConnectionError, ValueError) as e:
    logger.warning(f'Research failed: {e}')
```

**Acceptance Criteria:**
- [ ] All except clauses are specific
- [ ] No bare `except Exception` remaining
- [ ] Logging differentiates between error types

---

## MEDIUM (Nice to Have)

### 7. Add Unit Tests
**Status:** Zero coverage
**Create:** `tests/test_*.py` files

**Suggested Tests:**
- test_factchecker.py: claim verification logic
- test_intent_extractor.py: gap detection
- test_analyzer.py: signal calculation
- test_feeds.py: deduplication
- test_models.py: validation

**Acceptance Criteria:**
- [ ] 70%+ code coverage
- [ ] Tests pass locally
- [ ] Can run with: `pytest tests/`

---

### 8. Add Structured Logging
**Status:** Plain text logging
**What:** Switch to JSON or structured format

**Consider:** python-json-logger or structlog

```python
# BEFORE
logger.info(f'[{i}/{total}] Story processed')

# AFTER
logger.info('story_processed', extra={
    'story_id': story.id,
    'index': i,
    'total': total,
    'confidence': factcheck.overall_confidence,
})
```

---

## Execution Order

1. **research.py** (CRITICAL) — Unblock the entire system
2. **Type hints** (CRITICAL) — Make code safe
3. **Input validation** (CRITICAL) — Prevent bad data
4. **SSL fix** (CRITICAL) — Security
5. **Config refactor** (HIGH) — Maintainability
6. **Error handling** (HIGH) — Robustness
7. **Tests** (MEDIUM) — Confidence
8. **Logging** (MEDIUM) — Observability

---

## Testing After Each Change

```bash
# After each module fix:
cd /home/r2d2/projects/news-engine
python3 -m py_compile news_engine/*.py  # Type check
python3 main.py --help                   # Entry point works
python3 main.py --dry-run --verbose      # Full pipeline test
```

---

## Commit Message Template

```
[news-engine] Fix: <component>

- <specific change>
- <specific change>

Addresses Yoda review: <issue number>
```

Example:
```
[news-engine] Fix: Add type hints to orchestrator

- Add return types to all public methods
- Add parameter types
- Import typing module

Addresses Yoda review: CRITICAL #3
```

---

## Report Back When

1. ✅ research.py is functional
2. ✅ All CRITICAL fixes complete
3. ✅ Code compiles with no errors
4. ✅ Tests pass (if added)

Then we can test the full pipeline and generate first edition.

---

**Command:** Start with research.py. Report progress.
