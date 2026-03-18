# Improve Current Maxwell Newspaper (Before SaaS)

**Goal:** Make today's "The Headlines Today" excellent before building tomorrow's platform.

**Approach:** Slow, methodical improvements. Quality first.

---

## Current State
- Runs daily at 5 AM EST
- 6 hardcoded RSS sources
- Fixed sections (World News, Tech, India, etc.)
- Lives at: news.suhailtaj.cloud

---

## Improvement Roadmap (No Timeline, Just Quality)

### 1. Better Feed Selection (Next)
**Current:** 6 hardcoded sources
```python
sources = {
    "World News": ["BBC World", "Reuters"],
    "AI & Tech": ["Hacker News", "BBC Tech"],
    "India": ["Times of India"],
    ...
}
```

**Improve:** Use awesome-rss-feeds repo
- [ ] Clone plenaryapp/awesome-rss-feeds
- [ ] Parse OPML files → JSON
- [ ] Hand-pick best feeds (not all 500, just curated ~30)
  - World News: BBC World, Reuters, AP
  - AI & Tech: Hacker News, TechCrunch, MIT Tech Review
  - India: Times of India, NDTV, The Hindu
  - Business: Financial Times, Bloomberg, WSJ
  - Trending: X.com trending topics
  - etc.

- [ ] Build `feed_selector.py` to intelligently pick feeds
  - Score by freshness, relevance, source authority
  - Prefer high-quality sources over volume

### 2. Add X.com Trending (Next)
**Current:** No social/trending section
**Add:** "What's Trending on X" section

**Implementation:**
- [ ] Create X account (use R2D2's birthday as DOB)
- [ ] Fetch trending topics via X API (or web scrape)
- [ ] For each trending topic: fetch 1-2 top tweets
- [ ] Claude (Maxwell) writes brief context: "Why is X trending?"
- [ ] Add to newspaper as "🔥 Trending" section

**Example Output:**
```
🔥 TRENDING ON X
─────────────────────
#OpenAI — Major AI Announcement Expected This Week
  Context: OpenAI posted cryptic teaser yesterday. Industry expects major 
  model release or partnership announcement...

#CrunchGPT — Developer Tool Launch
  Context: New AI tool helps engineers write code 50% faster. HN #1 
  trending, 5K upvotes...
```

### 3. Yoda Reviews Article Quality (Ongoing)
**Current:** Maxwell produces articles, no quality review
**Add:** Yoda checks every edition

**Process:**
- [ ] After Maxwell generates edition, run Yoda check:
  - Are headlines compelling but not clickbait?
  - Is lede (first sentence) the most important fact?
  - Is body 150-200 words (not too long/short)?
  - No opinion, all facts attributed?
  - Kicker (last sentence) hints at what's next?

- [ ] Yoda returns:
  - ✅ Edition approved
  - 🟡 X articles need tweaking (specific feedback)
  - ❌ Reject, regenerate (rare)

**Yoda's Checklist:**
```
✓ Headlines: Active voice, < 10 words, no hype
✓ Lede: Single most important fact, one sentence
✓ Body: 150-200 words, inverted pyramid, attributed
✓ Kicker: Forward-looking, one sentence
✓ Tone: Neutral, no adjectives ("shocking", "alarming")
✓ Uniqueness: No near-duplicates
✓ Freshness: < 48h old (+ exception context)
```

### 4. Better Story Selection (Ongoing)
**Current:** ~30 raw articles → ~8-12 curated
**Improve:** Smarter de-duplication and ranking

- [ ] Same story from multiple sources → pick best version
- [ ] Rank by: Importance, uniqueness, timeliness, source authority
- [ ] Balance sections: Don't overweight any category
- [ ] Human eye: Suhail manually reviews, gives feedback
- [ ] Iterate based on feedback

**Example:**
- Raw: "Apple Releases New iPhone" (5 sources)
- Pick: Reuters version (most balanced + technical detail)
- Rank high, include once

### 5. Editorial Polish (Ongoing)
**Current:** Claude writes all copy
**Improve:** Human review + iteration

- [ ] Suhail reads edition each morning
- [ ] Marks issues: "This headline is weak", "This story doesn't matter", "Add more context"
- [ ] R2D2 logs feedback
- [ ] Yoda + Maxwell iterate based on patterns
- [ ] Gradually refine what matters to Suhail

**Feedback Loop:**
```
Maxwell generates → Suhail reads → Logs feedback
                                        ↓
                                    Yoda analyzes patterns
                                        ↓
                                  Maxwell learns to:
                                  - Pick better stories
                                  - Write better headlines
                                  - Balance sections differently
```

### 6. Add Explainers & Context (Optional)
**Current:** News headline + summary
**Add:** "Why this matters" section for complex topics

**Example:**
```
HEADLINE: Federal Reserve Raises Interest Rates 0.25%

WHAT HAPPENED: The Fed increased rates from 4.5% to 4.75%.

WHY IT MATTERS: 
- Your savings account yields go up (good)
- Mortgages get more expensive (bad for buyers)
- Stock market may dip short-term (normal)
- Inflation should slow over 6-12 months

WHAT TO WATCH: If inflation stays high, more increases likely.
```

### 7. A/B Test Sections (Optional)
**Current:** Fixed 6 sections daily
**Test:** What sections does Suhail actually read?

- [ ] Add tracking: Which articles opened? Which read fully?
- [ ] Adjust section order based on engagement
- [ ] Drop low-engagement sections
- [ ] Expand high-engagement sections

---

## Implementation Order (Slow & Steady)

### Week 1
- [ ] Clone awesome-rss-feeds, hand-pick 30 feeds
- [ ] Update maxwell.py to use new feeds
- [ ] Test: Run maxwell.py, review output manually

### Week 2
- [ ] Create X account (R2D2's identity)
- [ ] Build trending fetcher (X API or web scrape)
- [ ] Add "Trending" section to Maxwell
- [ ] Test: Review with trending included

### Week 3
- [ ] Integrate Yoda quality check
- [ ] Add Yoda's review prompt to Maxwell pipeline
- [ ] Test: Generate edition, get Yoda feedback
- [ ] Iterate based on feedback

### Week 4+
- [ ] Suhail reads daily, logs feedback
- [ ] R2D2 patterns analysis
- [ ] Adjust story selection + headlines
- [ ] Polish iteratively

---

## Success = Quality, Not Speed

**Metrics:**
- ✅ Suhail reads 90%+ of articles (was probably 40-50% before)
- ✅ Zero clickbait headlines
- ✅ All stories matter (no filler)
- ✅ Trending section adds value
- ✅ Yoda finds 0 quality issues

**Not about:**
- Adding 10 new features
- Launching SaaS ASAP
- Growth metrics

Just: **Make it excellent.**

---

## Questions

1. What's your actual birth date (for R2D2's DOB)?
2. Which X account should I create?
3. Which 5-10 feeds do you ALWAYS want included?
4. What sections matter most to you?
5. How much time can you spend on feedback daily?

---

*Once the daily newspaper is excellent, then we scale to SaaS. Not before.*
