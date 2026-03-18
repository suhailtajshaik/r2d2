# News Engine Code Review — Yoda's Analysis

**Request:** Review News Engine v2.0 codebase for quality, best practices, security, and architecture.

**Codebase:** `/home/r2d2/projects/news-engine/`

---

## Code Quality & Best Practices Review (Yoda Analysis)

### 1. orchestrator.py (Main Pipeline)

**Strengths:**
- ✅ Clean separation of concerns (fetch → parallel analysis → synthesize)
- ✅ ThreadPoolExecutor used correctly for parallel execution
- ✅ Error handling with try/except on each story
- ✅ Logging at each step
- ✅ JSON serialization is clean

**Issues to Address:**

❌ **Missing Type Hints**
- Lines 28-33: Constructor has no return type
- `generate_edition()`, `_analyze_story_parallel()` need return types
- Function parameters need type hints

❌ **Magic Numbers**
- Line 98: `max_workers=4` is hardcoded (should be configurable)
- Line 137: `story.title[:50]` truncation magic (repeated 3 times)

❌ **Error Handling Too Broad**
- Line 104: Catches `Exception` (too broad) → catch specific exceptions
- Line 111: Same issue
- Should handle `PerplexityError`, `FactCheckError`, `IntentError` separately

❌ **Resource Leaks Potential**
- Line 88: ThreadPoolExecutor used correctly, but no timeout on executor.submit()
- Could hang if task takes too long

❌ **Logging Issues**
- Line 94: `logger.info(f'[{i}/{len(raw_stories)}] ✓...')` — i might be out of order (parallel execution)
- Consider using unique story ID instead

### 2. factchecker.py (Fact-Checking Logic)

**Strengths:**
- ✅ Clear, understandable logic
- ✅ Good red flag detection heuristics
- ✅ Confidence calculation is transparent

**Issues to Address:**

❌ **Hardcoded Source Credibility**
- Lines 83-89: Credibility scores hardcoded in method
- Should be in config or database
- Makes it hard to update (new sources, rebranding)

❌ **Weak Claim Extraction**
- Lines 52-59: Simple heuristics (just headlines + first 2 sentences)
- Real claims need NLP or Claude for extraction
- Current approach misses nuanced claims

❌ **Magic Confidence Numbers**
- Line 60: 95%, 85%, 70%, 30% hardcoded
- Line 73: confidence - 20 penalty hardcoded
- Line 97: min(99, base_score + 10) — why 99? Why +10?
- All should be configurable

❌ **No Claim Deduplication**
- Multiple stories might extract same claim
- No dedup before verification

### 3. intent_extractor.py (Intent Analysis)

**Strengths:**
- ✅ Good gap analysis (impact, context, responses, human stories)
- ✅ Clear intent understanding logic
- ✅ Narrative identification

**Issues to Address:**

❌ **Hardcoded Keywords**
- Lines 63-66: `['impact', 'effect', 'official', 'statement']` hardcoded
- Lines 76-77: `['people', 'civilian']` hardcoded
- Lines 80-81: `['next', 'will']` hardcoded
- Should be configuration

❌ **Shallow Timeline Analysis**
- Line 47: Only counts timeline length
- Doesn't analyze gaps between dates
- Doesn't detect if reporting went silent then resurfaced

❌ **No Context Extraction from Content**
- Relies only on story text word frequency
- Should use Claude to extract actual context

### 4. analyzer.py (Synthesis Logic)

**Strengths:**
- ✅ Clear signal combination logic
- ✅ Transparent confidence calculation

**Issues to Address:**

❌ **Signal Score Calculation**
- Lines 97-116: Hardcoded signal weights (90, 75, 40, 85, 70, 50, 65, 80)
- No justification for weights
- Makes tuning impossible

❌ **No Weighting Explanation**
- Why is research signal [0] = 90/75/40?
- Why is fact-check signal [1] = always confidence?
- Why is intent signal [2] = contradictions-based?

❌ **Missing Combined Analysis**
- Doesn't check for contradictions between streams
- E.g., high confidence but low corroboration → should flag

### 5. feeds.py (RSS Fetching)

**Strengths:**
- ✅ Good error handling per feed
- ✅ SSL context bypass is documented (for testing)
- ✅ Item limit prevents overload

**Issues to Address:**

❌ **SSL Context Bypass**
- Line 31-34: `verify_mode = ssl.CERT_NONE` is dangerous in production
- Should use proper certificate verification
- At least make it configurable

❌ **No Rate Limiting**
- Fetches all feeds simultaneously
- No delays between requests
- Could trigger rate limits or be seen as DDoS

❌ **No Retry Logic**
- Feed fails once → skipped forever that run
- Should retry with backoff

### 6. research.py (Perplexity Integration)

**Issues to Address:**

❌ **STUB IMPLEMENTATION**
- Entire module is a stub
- Returns dummy data (not real research)
- Critical for whole system!

**Action Required:**
- Integrate actual `web_search` tool
- Implement corroboration search
- Implement timeline extraction
- Implement contradiction detection

### 7. config.py (Configuration)

**Strengths:**
- ✅ Dataclass-based config is clean
- ✅ Type hints present

**Issues to Address:**

❌ **Hardcoded Defaults**
- No environment variable support
- Can't override at runtime
- Should support: YAML, env vars, CLI flags

❌ **No Validation**
- Config loaded but not validated
- No checks for: min_confidence > 0, require_sources > 0
- Could silently fail with bad config

### 8. models.py (Data Models)

**Strengths:**
- ✅ Clean dataclass usage
- ✅ Good separation of concerns

**Issues to Address:**

❌ **No Validation**
- Confidence scores could be > 100 or < 0
- No type checking on list items

---

## Security Review

❌ **SSL Verification Disabled**
- feeds.py line 34: `verify_mode = ssl.CERT_NONE`
- Risk: MITM attacks on RSS feeds
- Fix: Use proper certificates

❌ **JSON Injection**
- Line 282 (orchestrator.py): `json.dump()` with `ensure_ascii=False`
- Low risk but should be careful
- Consider: `json.dumps(..., default=str)` for type safety

❌ **No Input Validation**
- Story title from RSS could contain malicious content
- No sanitization before logging or storing
- Fix: Use logging that escapes special chars

---

## Performance Review

✅ **Good:** Parallel execution (ThreadPoolExecutor)
✅ **Good:** Feed deduplication
❌ **Bad:** No caching of research results (same story researched each run)
❌ **Bad:** No database (everything in memory)
❌ **Bad:** No pagination (fetches all stories at once)

---

## Testing & Observability

❌ **No Unit Tests**
- Zero test coverage
- No test files

❌ **Logging Could Be Better**
- No structured logging (only text)
- No log levels (all info)
- Hard to parse machine-readable

❌ **No Metrics**
- No timing metrics
- No success/failure rates
- No CI/CD integration

---

## Summary: Priority Fixes

### CRITICAL (Must Fix Before Production)
1. ✅ Implement research.py (web_search integration)
2. ❌ Fix SSL verification in feeds.py
3. ❌ Add input validation on all modules
4. ❌ Add comprehensive error handling (not Exception)

### HIGH (Before Major Release)
1. ❌ Add type hints to all functions
2. ❌ Make hardcoded values configurable
3. ❌ Add unit tests (minimum 70% coverage)
4. ❌ Add structured logging
5. ❌ Implement caching for research results

### MEDIUM (Nice to Have)
1. ❌ Add CLI argument parsing for all config
2. ❌ Add database backend
3. ❌ Add metrics/observability
4. ❌ Add rate limiting for feeds
5. ❌ Improve claim extraction (use Claude)

---

## Code Review Checklist (for 3PO)

### orchestrator.py
- [ ] Add type hints to all functions
- [ ] Make max_workers configurable
- [ ] Add timeout to ThreadPoolExecutor tasks
- [ ] Use specific exception handling
- [ ] Fix logging index issue in parallel loop
- [ ] Extract magic string lengths to constants

### factchecker.py
- [ ] Move source credibility to config
- [ ] Make confidence scores configurable
- [ ] Add real claim extraction (use Claude)
- [ ] Add claim deduplication

### intent_extractor.py
- [ ] Move keyword lists to config
- [ ] Improve timeline analysis
- [ ] Add Claude-powered context extraction

### analyzer.py
- [ ] Document signal weights
- [ ] Make weights configurable
- [ ] Add contradiction detection between streams

### feeds.py
- [ ] Remove SSL bypass (or make configurable)
- [ ] Add retry logic with backoff
- [ ] Add rate limiting

### research.py
- [ ] Implement web_search integration
- [ ] Add proper error handling

### config.py
- [ ] Add environment variable support
- [ ] Add config validation
- [ ] Add CLI argument support

### models.py
- [ ] Add value validation
- [ ] Add __post_init__ checks

### Overall
- [ ] Add unit tests (test/, pytest.ini)
- [ ] Add structured logging
- [ ] Add type checking (mypy)
- [ ] Add linting (flake8, pylint)

---

## Yoda's Verdict

**Overall Grade: B+ (Good Foundation, Needs Hardening)**

### What's Good
- ✅ Clean architecture (pipeline model works well)
- ✅ Parallel execution is smart
- ✅ Logical separation of concerns
- ✅ No circular dependencies

### What Needs Work
- ❌ Too many hardcoded values
- ❌ Missing type hints
- ❌ No error handling specificity
- ❌ No tests or validation
- ❌ research.py is a stub

### Recommendation
**READY FOR INTEGRATION** once research.py is implemented, but needs hardening before production use.

Priority: Get research.py working → Then add type hints → Then tests.

---

*Yoda has spoken. Now dispatch 3PO to execute these changes.*
