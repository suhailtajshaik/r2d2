# 3PO Code Review Process

## Workflow
1. **3PO writes code** (Claude Code)
2. **3PO self-reviews** (checks against standards)
3. **Yoda reviews** (expert second opinion)
4. **R2D2 reports** to Suhail with Yoda's wisdom

## Integration
After 3PO completes work:

```bash
# 3PO writes code
claude --print 'build a feature' 

# Then R2D2 asks Yoda
ask_yoda.py "Review this code for [code-snippet]"
```

## What Yoda Reviews
- ✅ API architecture (backend proxy pattern?)
- ✅ Code quality (SOLID violations?)
- ✅ Security (keys exposed? CORS issues?)
- ✅ Performance (N+1 queries? Inefficient loops?)
- ✅ Testing (coverage? edge cases?)
- ✅ Best practices (matches code-review-checklist.md?)

## Yoda's Output
- Specific issues found
- Citations from knowledge base
- Actionable fixes
- Risk assessment (blocker vs nice-to-have)

## Example
```
3PO: [writes 500-line React component]

R2D2: "Yoda, review this for security and performance"

Yoda: "Found 3 issues:
1. API key in .env.public (CRITICAL - api-architecture-mistake.md)
2. N+1 database queries (PERFORMANCE - training_insights.md)
3. Missing error boundaries (QUALITY)

Recommend: Fix 1 & 2 before ship, 3 is optional."
```

## Rules
- **Always consult Yoda** before shipping code
- **Never skip Yoda's review** — he catches what humans miss
- **Cite sources** — Yoda backs up advice with learned lessons
- **Act on blockers** — fix critical issues, negotiate nice-to-haves
