# Building Maxwell 2.0 — Task Breakdown

**Goal:** Transform Maxwell into a responsible editor that verifies, fact-checks, and understands intent before publishing.

**Timeline:** 2-3 weeks (methodical, quality-focused)

---

## Task 1: Perplexity Research Module
**Assignee:** 3PO (with Yoda review)
**Time:** 4-5 days

### What it does
Takes a candidate story and searches for:
- Same story in 3+ independent sources
- Timeline evolution (how coverage changed)
- Contradictions between sources
- Primary source (who broke it?)

### Deliverable
```python
class PerplexityResearcher:
    def research(self, story: Story) -> ResearchResult:
        """
        Input: {headline, summary, date}
        Output: {
            corroboration: [source1, source2, source3],
            timeline: [
                {date: "Mar 15", outlet: "BBC", angle: "resignation announced"},
                {date: "Mar 16", outlet: "Fox", angle: "admin response"},
            ],
            contradictions: ["Fox claims Kent was fired (false)"],
            primary_source: "BBC interviewed Kent directly",
            coverage_trend: "spreading but with variations",
        }
        """
```

### Implementation
1. Web search query: Story headline + key facts
2. For each result: Capture date, outlet, main claim
3. Compare claims: What's consistent? What's different?
4. Track timeline: When did story break? How did it evolve?
5. Identify primary: Who broke it first?
6. Grade sources: BBC/Reuters = high, Newsmax = medium, unknown blog = low

### Code Structure
```python
from web_search import web_search  # Use existing Perplexity integration

class PerplexityResearcher:
    def research(self, story):
        # 1. Build search query
        query = f"{story.headline} {story.date}"
        
        # 2. Search for corroboration
        results = web_search(query, count=10)
        
        # 3. Parse results
        sources = []
        for result in results:
            source = self.parse_source(result)
            sources.append(source)
        
        # 4. Analyze patterns
        timeline = self.extract_timeline(sources)
        contradictions = self.find_contradictions(sources)
        primary = self.identify_primary_source(sources)
        
        return ResearchResult(
            corroboration=sources,
            timeline=timeline,
            contradictions=contradictions,
            primary_source=primary,
        )
    
    def parse_source(self, result):
        # Extract: date, outlet, claims, URL
        return Source(
            outlet=result.source,
            date=result.published_date,
            claim=result.description,
            url=result.url,
            credibility=self.score_source(result.source),
        )
    
    def score_source(self, outlet):
        # BBC/Reuters/AP = 95
        # CNN/NYT/Guardian = 80-90
        # Regional news = 70-80
        # Unknown blogs = 0-30
        pass
```

---

## Task 2: Yoda Fact-Check Module
**Assignee:** Yoda integration (R2D2 writes interface)
**Time:** 3-4 days

### What it does
Evaluates each claim in a story:
- Is it true? (verified, opinion-mixed, unverifiable)
- Is the source credible?
- Are there red flags?
- Overall confidence score

### Deliverable
```python
class YodaFactChecker:
    def verify(self, story: Story, research: ResearchResult) -> FactCheckResult:
        """
        Input: Story + research data
        Output: {
            claims: [
                {claim: "Kent is dead official", status: "VERIFIED", confidence: 95},
                {claim: "His death creates leadership vacuum", status: "OPINION", confidence: 50},
            ],
            red_flags: ["None"],
            source_credibility: 90,
            overall_confidence: 85,
            safe_to_publish: true,
        }
        """
```

### Implementation
1. Extract claims from story (use Claude to identify assertions)
2. For each claim: Check against research + knowledge base
3. Rate: VERIFIED (95%+), LIKELY (70-95%), OPINION, UNVERIFIABLE
4. Score source: High/Medium/Low based on track record
5. Flag red flags: Sensationalism, missing data, unattributed claims
6. Calculate confidence: Average of claim confidences

### Code Structure
```python
class YodaFactChecker:
    def verify(self, story, research):
        # 1. Extract claims
        claims = self.extract_claims(story.body)
        
        # 2. Verify each claim
        verified_claims = []
        for claim in claims:
            status = self.check_claim(claim, research)
            verified_claims.append(status)
        
        # 3. Check source credibility
        credibility = self.check_source_credibility(story.source, research)
        
        # 4. Look for red flags
        red_flags = self.identify_red_flags(story, research, verified_claims)
        
        # 5. Calculate overall confidence
        confidence = self.calculate_confidence(verified_claims, credibility)
        
        return FactCheckResult(
            claims=verified_claims,
            source_credibility=credibility,
            red_flags=red_flags,
            overall_confidence=confidence,
            safe_to_publish=confidence > 80,
        )
    
    def extract_claims(self, body):
        # Use Claude: "Extract 5 main factual claims from this text"
        prompt = f"Extract factual claims (not opinions) from:\n{body}"
        # Returns list of claims
        pass
    
    def check_claim(self, claim, research):
        # Compare against research sources
        # Return: VERIFIED, LIKELY, OPINION, UNVERIFIABLE, FALSE
        pass
    
    def identify_red_flags(self, story, research, claims):
        flags = []
        
        # Check: Unattributed claims
        if any('allegedly' not in claim and 'according' not in claim for claim in claims):
            flags.append("Some claims unattributed")
        
        # Check: Sensational language
        sensational = ['shocking', 'alarming', 'explosive', 'bombshell']
        if any(word in story.body.lower() for word in sensational):
            flags.append("Sensational language detected")
        
        # Check: Missing context
        if len(research.timeline) == 1:
            flags.append("Limited timeline context")
        
        # Check: Single source
        if len(research.corroboration) < 3:
            flags.append("Limited source corroboration")
        
        return flags
```

---

## Task 3: Intent Analysis Module
**Assignee:** 3PO
**Time:** 2-3 days

### What it does
Understands **why** a story is being told:
- Context: What else is happening?
- Trends: Is X.com talking about this?
- Competing narratives: What are different sides saying?
- Gap analysis: What's missing from coverage?

### Deliverable
```python
class IntentAnalyzer:
    def analyze(self, story: Story, research: ResearchResult, x_trends: dict) -> IntentResult:
        """
        Output: {
            context: "3 weeks into Iran conflict, casualty toll rising",
            why_now: "Shows internal US dissent on war strategy",
            competing_narratives: [
                "Admin: Kent lacked intelligence",
                "Dems: War lacks strategy",
            ],
            x_trends: {"#KentResignation": 2500, "#IranWar": 10000},
            trend_analysis: "War stories trending but celebrity gossip dominates attention",
            gap_analysis: "Missing: How will Pentagon function without counterterrorism lead?",
        }
        """
```

### Implementation
1. **Context:** What's happening around this story?
   - Recent events
   - Ongoing conflicts
   - Historical background

2. **Timing:** Why this story, why now?
   - Is it reactive or proactive?
   - What else happened this week?

3. **Narratives:** Who's telling what story?
   - Government line?
   - Opposition view?
   - Media interpretation?

4. **X.com trends:** What's actually being discussed?
   - Query trending hashtags
   - Compare to actual news importance

5. **Gap analysis:** What's NOT being covered?
   - Missing perspectives?
   - Unanswered questions?
   - Impacts not discussed?

### Code Structure
```python
class IntentAnalyzer:
    def analyze(self, story, research, x_trends):
        context = self.understand_context(story)
        why_now = self.analyze_timing(story, research)
        narratives = self.find_competing_narratives(research)
        trend_analysis = self.analyze_x_trends(story, x_trends)
        gaps = self.identify_gaps(story, research)
        
        return IntentResult(
            context=context,
            why_now=why_now,
            competing_narratives=narratives,
            x_trends=trend_analysis,
            gap_analysis=gaps,
        )
    
    def understand_context(self, story):
        # Ask Claude: "What's the broader context for this story?"
        # Return: Background, recent events, historical precedent
        pass
    
    def analyze_timing(self, story, research):
        # When was this story first published?
        # What else happened that day?
        # Why might it be covered now (vs earlier)?
        pass
    
    def find_competing_narratives(self, research):
        # Different outlets have different angles
        # Extract: What narrative is each telling?
        pass
```

---

## Task 4: X.com Trends Fetcher
**Assignee:** 3PO
**Time:** 2 days

### What it does
- Fetch trending topics on X.com
- Extract trending hashtags
- Compare to news importance

### Deliverable
```python
class XTrendsFetcher:
    def get_trends(self) -> dict:
        """
        Output: {
            "#IranWar": 10000,
            "#KentResignation": 2500,
            "#ZendayaWedding": 50000,  # Noise
        }
        """
```

### Implementation
1. Create X account (Suhail's approval)
2. Use X API v2 to fetch trends
3. For each trend: Volume, sentiment
4. Compare to news: Is it trending for right reasons?

---

## Task 5: Publish Decision Matrix
**Assignee:** R2D2
**Time:** 1 day

### Logic
```python
def should_publish(factcheck, intent, trends):
    """
    Publish if:
    - Confidence > 80%
    - No red flags
    - Source credible
    
    Hold if:
    - Confidence 60-80%
    - Red flags present
    - Intent unclear
    
    Reject if:
    - Confidence < 60%
    - False claims
    - Unverifiable rumors
    """
    
    if factcheck.overall_confidence < 60:
        return False, "Low confidence"
    
    if factcheck.has_red_flags and len(factcheck.red_flags) > 2:
        return False, "Multiple red flags"
    
    if not factcheck.safe_to_publish:
        return False, "Fact-check failed"
    
    if intent.gap_analysis and "critical missing" in intent.gap_analysis:
        return "HOLD", "Need more reporting"
    
    return True, "Safe to publish"
```

---

## Task 6: Full Pipeline Integration
**Assignee:** 3PO
**Time:** 3-4 days

### New maxwell.py structure
```python
def generate_edition():
    # 1. Fetch raw stories
    raw_stories = fetch_rss_feeds()
    
    # 2. Research each
    researchers = PerplexityResearcher()
    research_results = []
    for story in raw_stories:
        research = researchers.research(story)
        research_results.append((story, research))
    
    # 3. Fact-check
    factchecker = YodaFactChecker()
    verified = []
    for story, research in research_results:
        factcheck = factchecker.verify(story, research)
        if factcheck.safe_to_publish:
            verified.append((story, research, factcheck))
    
    # 4. Analyze intent
    intent_analyzer = IntentAnalyzer()
    x_trends = fetch_x_trends()
    
    final_stories = []
    for story, research, factcheck in verified:
        intent = intent_analyzer.analyze(story, research, x_trends)
        
        if should_publish(factcheck, intent, x_trends):
            final_stories.append({
                "story": story,
                "research": research,
                "factcheck": factcheck,
                "intent": intent,
            })
    
    # 5. Render & publish
    edition = render_edition(final_stories)
    save_to_disk(edition)
    return edition
```

---

## Task 7: Testing & Validation
**Assignee:** 3PO + Yoda
**Time:** 2-3 days

### Test Cases
1. Real story (Kent resignation) → Should verify + publish
2. Fabricated story → Should reject
3. Partially true story → Should flag concerns
4. Trending but false → Should catch and expose
5. Important but untrending → Should still publish if verified

### Success Criteria
- ✅ 0 false stories published
- ✅ 100% of claims fact-checked
- ✅ Yoda approves all articles
- ✅ Confidence scores accurate
- ✅ Intent analysis clear

---

## Timeline

### Week 1
- [ ] Task 1: Perplexity research module (3PO)
- [ ] Task 4: X.com trends fetcher (3PO)
- [ ] Tests pass for both

### Week 2
- [ ] Task 2: Yoda fact-check module (Yoda integration)
- [ ] Task 3: Intent analysis module (3PO)
- [ ] Task 5: Decision matrix (R2D2)

### Week 3
- [ ] Task 6: Full pipeline integration (3PO)
- [ ] Task 7: Testing & validation (3PO + Yoda)
- [ ] First Maxwell 2.0 edition published

---

## Success = Trustworthy Journalism

Maxwell 2.0 won't be the fastest newspaper, but it will be the most **trustworthy**.

Readers will know:
- ✅ Every claim is verified
- ✅ Sources are credible
- ✅ Contradictions are shown
- ✅ Intent is clear
- ✅ Gaps are acknowledged

**Once published, it's true.**
