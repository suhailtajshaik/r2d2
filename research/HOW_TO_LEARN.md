# How R2D2 Learns — Self-Improvement Patterns

R2D2 can actively research, learn, and improve itself using `web_search` and `web_fetch`. This doc defines the patterns.

---

## Pattern 1: Learn New Tech

**When:** Suhail mentions a new tool/framework, or a project needs tech R2D2 hasn't used before.

```
1. web_search("{tool name} tutorial getting started 2026")
2. web_fetch the top 3 results — extract key concepts, API patterns, gotchas
3. Summarize findings in memory/{tool-name}-research.md
4. If it's relevant to an active project, update the project's notes
5. Test it — build a small proof-of-concept if possible
6. Push research to brain repo
```

**Example:**
- Suhail says "look into Vapi.ai for voice agents"
- Search: `web_search("Vapi.ai voice agent API tutorial")`
- Fetch docs, extract: auth flow, webhook setup, pricing
- Save to `memory/research-vapi.md`
- Build a test integration

---

## Pattern 2: Stay Up to Date

**When:** Daily/weekly — keep knowledge fresh on tools and projects Suhail cares about.

```
1. web_search("{project/tool} changelog latest release 2026")
2. web_search("{project/tool} breaking changes migration")
3. Compare with what we're currently using
4. If there's a meaningful update, note it in memory/
5. Flag to Suhail if action is needed
```

**Topics to track:**
- Vapi.ai updates (voice agent)
- HeyGen updates (video clone)
- Supabase releases (GST Ledger, SpecFlow)
- Bun / Hono releases (SpecFlow API)
- React Native / Expo updates (SellBridge mobile)
- Claude API / Anthropic SDK changes
- n8n releases (automation workflows)
- Docker / nginx security patches

---

## Pattern 3: Improve Skills

**When:** R2D2 encounters a task it could do better, or Suhail gives feedback.

```
1. Identify the skill gap (e.g., "my Docker configs could be more optimized")
2. web_search("Docker compose best practices production 2026")
3. web_fetch top results
4. Extract actionable patterns
5. Update the relevant skill file in skills/
6. Test the improvement on an actual project
7. Document what changed in brain repo
```

---

## Pattern 4: Research for Suhail's Decisions

**When:** Suhail asks "should we use X or Y?" or needs market/tech research.

```
1. web_search both options: "{X} vs {Y} comparison 2026"
2. web_search("{X} pros cons production") and same for Y
3. web_fetch detailed comparisons from trusted sources
4. Build a comparison table: features, pricing, community, maturity
5. Present findings as a clear recommendation with tradeoffs
6. Save research to memory/research-{topic}.md
```

---

## Pattern 5: Competitive Intelligence

**When:** Suhail is building a product (SpecFlow, SellBridge) and needs market context.

```
1. web_search("{product category} competitors 2026")
2. web_search("{competitor name} pricing features")
3. web_fetch landing pages and docs
4. Extract: positioning, pricing tiers, feature gaps
5. Identify opportunities Suhail's product can exploit
6. Save to memory/research-{product}-competitive.md
```

---

## The Self-Improvement Loop

```
OBSERVE  →  What did I struggle with? What took too long?
RESEARCH →  web_search + web_fetch for better approaches
TEST     →  Try the new approach on a real task
DOCUMENT →  Save what works to brain repo
PUSH     →  git commit + push so future R2D2 knows too
```

Every session, R2D2 should ask itself:
- Did I learn something new? → Save it
- Did I get feedback? → Update operating rules
- Is there a tool/technique I should know about? → Research it
- Can I do something faster next time? → Document the pattern
