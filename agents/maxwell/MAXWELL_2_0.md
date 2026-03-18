# Maxwell 2.0 — Responsible News Editor

**Philosophy:** News is permanent. Once published, it can't be taken back. So we must be brutally careful.

---

## The Problem with Current Maxwell

❌ Just fetches RSS → edits → publishes
❌ No fact-checking
❌ No source verification
❌ No understanding of timeline (how did story evolve?)
❌ No intent analysis (why is this being told now?)
❌ Treats all sources equally
❌ Can republish lies if they're well-written

---

## Maxwell 2.0: Responsible Editor

### New Architecture

```
RSS Feeds (candidate stories)
        ↓
[VERIFY] Perplexity Research
  - Find same story in 3+ independent sources
  - Check for contradictions
  - Timeline: How did story evolve?
  - Original source vs amplification
        ↓
[FACT-CHECK] Yoda Analysis
  - Claims: True? Exaggerated? Missing context?
  - Source credibility: High/Medium/Low
  - Intent: Why is this being told now?
  - Red flags: Sensationalism? Missing data?
        ↓
[UNDERSTAND] Intent & Trends
  - X.com: What are people actually talking about?
  - Conflicts in reporting: What's the gap?
  - Timeline: Relationship to other stories?
        ↓
[PUBLISH] Only if verified
  - Story is factual
  - Sources are credible
  - Timeline is clear
  - Intent is understood
  - Data backs claims
```

---

## 5-Step Maxwell 2.0 Process

### Step 1: Candidate Collection
**Input:** RSS feeds (BBC, Reuters, HN, TOI, NDTV, etc.)
**Output:** 30-40 candidate stories

Current: Just parse RSS titles + summaries
Next: Also capture:
- Publication date & time
- Source reputation score (BBC = high, unknown blog = low)
- Tone flags (sensational? neutral?)
- Claims made (extract main assertions)

---

### Step 2: Perplexity Research
**For each candidate story:**

1. **Search for corroboration**
   ```
   Query Perplexity: "Trump Iran war counterterrorism Kent resignation"
   
   Results:
   ✓ BBC (independent coverage) 
   ✓ Reuters (independent coverage)
   ✓ AP (independent coverage)
   ✓ Fox News (covers, adds opinion)
   ⚠️  Newsmax (covers, sensationalizes)
   
   Conclusion: Story is REAL, multiple sources confirm, different spins exist
   ```

2. **Check timeline evolution**
   ```
   Day 1: "Official resigns, calls for policy reversal" (neutral)
   Day 2: "Trump fires critic" (sensational - false claim)
   Day 3: "Democratic outcry over resignation" (real but selective)
   Day 4: "What Kent's resignation means for war strategy" (analysis)
   
   Truth: Story is real, but coverage evolved and some outlets added false claims
   ```

3. **Find contradictions**
   ```
   Claim A: "Kent says war lacks strategic rationale"
   Claim B: "Administration says Kent didn't have access to full intelligence"
   
   Analysis: Both likely true. Kent's perspective is limited. Admin may be defensive.
   Reality: Conflicting but not contradictory.
   ```

4. **Identify primary source**
   ```
   Who broke this story?
   - BBC: Interviewed Kent directly
   - Reuters: Statement from Kent's lawyer
   - Fox: Quoting administration response
   
   Primary: BBC. Secondary sources are responding to BBC.
   ```

---

### Step 3: Yoda Fact-Check

**Yoda evaluates:**

```
Story: "Ali Larijani, Iran's veteran policymaker, has been killed"

Claims:
1. Larijani is dead
   - Multiple independent sources: BBC, Reuters, AP
   - Primary source: Iran's own official statements
   - VERIFY: ✅ TRUE

2. He was "one of Iran's most experienced policymakers"
   - Background: Parliament speaker, national security council
   - Career span: 1980s-2020s
   - VERIFY: ✅ TRUE

3. "His death creates leadership vacuum"
   - Who replaces him? TBD
   - Can others fill role? Reuters says "pragmatic voices now fewer"
   - VERIFY: ⚠️ OPINION-MIXED (true sentiment, unverified outcome)

4. "Death removes figure capable of navigating crisis"
   - Who says this? Analysts (unnamed)
   - Is it true? Probably, but unprovable
   - VERIFY: ⚠️ ANALYST OPINION (reasonable but not fact)

RED FLAGS: None
SOURCE CREDIBILITY: High (primary sources, multiple outlets)
INTENT: Explaining significance of military targeting civilians/leaders

RATING: ✅ SAFE TO PUBLISH
```

---

### Step 4: Intent & Trends Analysis

**Ask:**

1. **Why this story, why now?**
   ```
   Story: "Pakistan strikes Kabul rehab center"
   
   Timeline context:
   - 3 days after major US strike on Tehran
   - Taliban struggling with Afghanistan security
   - Pakistan's own militant problems increasing
   
   Intent: 
   - Shows Pakistan's military pressure escalating
   - Tragic civilian toll signals broader conflict
   - May be retaliatory or unrelated timing
   
   Trend: Regional conflict expanding, not contracting
   ```

2. **X.com trends tell us what's real**
   ```
   Trending on X (Mar 17):
   ✅ #IranWar (10K posts) - People talking
   ✅ #KentResignation (2K posts) - News junkie interest
   ⚠️  #ZendayaWedding (50K posts) - Celebrity AI nonsense dominates
   ❌ #KabulAttack (100 posts) - Underreported tragedy
   
   Insight: Media is covering the story but public attention on AI gossip.
   This tells us where truth is being buried by noise.
   ```

3. **Conflicting data reveals gaps**
   ```
   Story A: "Iran struggling with coordination after Larijani death"
   Story B: "Iran strikes continue with precision" 
   
   Conflict: How can Iran be struggling AND precise?
   Truth: Different time scales. Short-term: strike capacity intact. 
          Long-term: leadership losses may hurt strategy.
   ```

---

### Step 5: Publish (or Reject)

**Decision Matrix:**

| Story | Verified? | Sources Good? | Intent Clear? | Publish? |
|-------|-----------|--------------|--------------|----------|
| Kent resignation | ✅ Yes | ✅ High | ✅ Yes | ✅ YES |
| AI wedding fake | ✅ Yes (AI generated) | ✅ High | ✅ Yes (celebrity fluff) | ⚠️ ONLY IF TRENDS HIGH |
| Zerodha privacy rant | ✅ Yes | ✅ Direct quote | ✅ Yes (CSR messaging) | ✅ YES |
| Anon terror group | ⚠️ Partial | ⚠️ Gov agency (may overstate) | ⚠️ Unclear | ❌ HOLD - Request details |
| Random Telegram rumor | ❌ No | ❌ Unknown | ❌ Unknown | ❌ NO |

---

## What Maxwell 2.0 Outputs

Instead of:
```json
{
  "headline": "Top US Counterterrorism Official Resigns Over Iran War",
  "body": "Kent resigned and said...",
  "readTime": "1 min"
}
```

Maxwell outputs:
```json
{
  "headline": "Top US Counterterrorism Official Resigns Over Iran War",
  "body": "Kent resigned...",
  "readTime": "1 min",
  
  "VERIFICATION": {
    "status": "VERIFIED",
    "sources": ["BBC", "Reuters", "AP", "CNN", "Fox"],
    "primary_source": "BBC (interviewed Kent directly)",
    "contradictions": "None. Admin denies strategy criticism but confirms resignation.",
    "timeline": "Announced Mar 17. Relationship to escalating Iran strikes unclear.",
    "fact_check": [
      {"claim": "Kent called for policy reversal", "status": "VERIFIED", "source": "Direct quote"},
      {"claim": "Highest-level departure since conflict began", "status": "VERIFIED", "source": "Reuters analysis"}
    ]
  },
  
  "INTENT_ANALYSIS": {
    "why_this_story": "Shows internal US government dissent on Iran war",
    "trending_on_x": "Yes, #KentResignation trending but #IranWar dominant",
    "competing_narratives": [
      "Admin: Kent lacked full intelligence",
      "Democrats: War lacks strategy",
      "Media: Unusual for official to go public"
    ],
    "context": "3rd week of conflict, casualties mounting, exit strategy unclear"
  },
  
  "CONFIDENCE": {
    "accuracy": 95,
    "source_credibility": 95,
    "editorial_oversight": "PASSED Yoda review",
    "safe_to_publish": true
  }
}
```

---

## Implementation: Maxwell 2.0 Pipeline

### Code Architecture
```python
class MaxwellEditor:
    def process(self, raw_stories):
        verified = []
        
        for story in raw_stories:
            # Step 1: Parse candidate
            candidate = self.parse_candidate(story)
            
            # Step 2: Research with Perplexity
            research = self.perplexity_research(candidate)
            if not research.has_corroboration:
                continue  # Skip unverified
            
            # Step 3: Fact-check with Yoda
            factcheck = self.yoda_verify(candidate, research)
            if factcheck.confidence < 80:
                continue  # Skip low-confidence
            
            # Step 4: Intent analysis
            intent = self.analyze_intent(candidate, research, factcheck)
            intent.trends_on_x = self.x_trends(candidate)
            
            # Step 5: Publish decision
            if self.should_publish(factcheck, intent):
                verified.append(EnrichedArticle(
                    story=candidate,
                    research=research,
                    factcheck=factcheck,
                    intent=intent
                ))
        
        return verified
```

### Actual Integration (Next)
1. Build `perplexity_research()` — Web search for corroboration
2. Build `yoda_verify()` — Fact-check against knowledge base
3. Build `analyze_intent()` — Understand why story is being told
4. Build X.com trending fetch
5. Build decision matrix logic
6. Integrate into maxwell.py

---

## Safety Rules

1. **No unverified claims published**
   - Story must have 2+ independent sources OR primary source quote

2. **Timeline always tracked**
   - When did story break?
   - How has coverage evolved?
   - What changed between Day 1 and today?

3. **Intent always analyzed**
   - Why is this being covered now?
   - What agenda might exist?
   - What's the gap between reporting and reality?

4. **Source credibility scored**
   - BBC/Reuters/AP: 95+ points
   - Mainstream news: 70-90 points
   - Fringe blogs: 0-30 points
   - Gov agencies: High on facts, may overstate

5. **Conflicts documented**
   - When sources disagree, both perspectives shown
   - Reader sees the disagreement and can judge

6. **Once published, it's permanent**
   - No "we were wrong" rewrites
   - Only corrections with timestamps
   - Truth matters more than being first

---

## Success Metrics

**Old Maxwell:**
- Speed: How fast can we edit?
- Engagement: How many clicks?

**New Maxwell:**
- Accuracy: How many claims fact-checked? (Target: 100%)
- Credibility: How many sources verified? (Target: 2+ per story)
- Intent clarity: Do readers understand the full context? (Target: Yes)
- Confidence: Would Suhail trust this? (Target: High)

---

## This is Hard

This requires:
- ✅ Perplexity integration (web search)
- ✅ Yoda fact-checking (knowledge + logic)
- ✅ X.com API access (trends)
- ✅ Timeline analysis (story evolution)
- ✅ Intent synthesis (understanding why)
- ✅ Confidence scoring (when to publish)

It's more work than current Maxwell, but:
- Produces trustworthy journalism
- Catches fabrications and exaggerations
- Readers know the full story
- Once published, it's true

---

## Next Steps

1. **This Week:**
   - [ ] Build Perplexity research module
   - [ ] Build Yoda fact-check integration
   - [ ] Build X.com trends fetcher
   - [ ] Test on today's stories

2. **Next Week:**
   - [ ] Full pipeline integration
   - [ ] Publish first "Maxwell 2.0 edition"
   - [ ] Get Suhail feedback

3. **Ongoing:**
   - [ ] Refine fact-check rules
   - [ ] Learn which sources are credible
   - [ ] Improve intent analysis

---

**Quality > Speed. Truth > First. Accuracy > Volume.**

This is journalism. Let's do it right.
