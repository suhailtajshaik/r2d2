# API Architecture Mistake — March 17, 2026

## The Problem
Prompt Studio was hitting Anthropic API rate limits repeatedly during dev work.

Root cause: **Frontend was making direct HTTP requests to Anthropic API with exposed API key.**

## Why It Happened
The code pattern (useTransform.js):
```javascript
// ❌ WRONG - Direct browser request
const response = await fetch('https://api.anthropic.com/v1/messages', {
  method: 'POST',
  headers: {
    'x-api-key': apiKey,  // ⚠️ Exposed in browser
  },
  body: JSON.stringify({ ... })
});
```

This creates multiple problems:
1. **No request deduplication** — same prompt sent twice = 2 API calls
2. **No caching** — repetitive testing hits API every time
3. **No retry logic** — 429 errors fail immediately, no backoff
4. **No per-user rate limiting** — server doesn't know who's calling
5. **Security risk** — API key visible in network tab
6. **CORS nightmare** — only works with `anthropic-dangerous-direct-browser-access` hack

## The Solution
**Always use a backend proxy:**

```
Frontend (React) 
  ↓ 
Backend Server (Node/Python)  [controls rate limiting, caching, retries]
  ↓ 
API Provider (Anthropic, etc.)
```

Backend handles:
- Request deduplication & caching
- Exponential backoff on 429
- Per-user/per-API-key rate limiting
- API key rotation
- Logging & monitoring
- Cost attribution

## Code Pattern (Correct)
Frontend: `POST /api/transform` → Backend routes to provider with retry logic

Backend (Node.js example):
```javascript
async function transformWithRetry(prompt, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'x-api-key': process.env.ANTHROPIC_API_KEY,  // ✅ Safe in .env
        },
        body: JSON.stringify({ ... })
      });
      
      if (response.status === 429) {
        const delay = Math.pow(2, i) * 1000; // Exponential backoff
        await new Promise(r => setTimeout(r, delay));
        continue;
      }
      return response;
    } catch (err) {
      if (i === maxRetries - 1) throw err;
    }
  }
}
```

## When to Use What
| Scenario | Solution |
|----------|----------|
| Production SaaS | Backend proxy (required) |
| Dev tool with user input | Backend proxy OR OpenRouter |
| One-off script | OpenRouter (simplest) |
| Internal tool, low traffic | Simple backend proxy OK |

## Prevention Checklist
- [ ] No API keys in frontend code (not even .env.public)
- [ ] All API calls go through backend proxy
- [ ] Backend has exponential backoff + retry logic
- [ ] Rate limiting is per-user, not global
- [ ] Cache repeated requests (same input = cached output)
- [ ] Monitor 429s — alert if threshold exceeded
- [ ] Code review: ask "does this expose an API key?"

## Applied To
- **Prompt Studio** — needs backend API router
- **Any future AI dev tool** — same pattern
- **All SaaS projects** — non-negotiable

---
*Learned hard way. Never again.*
