# Lesson: Nginx + SPA Reverse Proxy Path Rewriting
**Date:** March 29, 2026
**Context:** Prompt Studio deployment failed due to nginx misconfiguration
**Status:** ❌ MISTAKE MADE → ✅ FIXED AND DOCUMENTED

---

## The Mistake (Complete Timeline)

### Phase 1: Wrong Layer (Code instead of Infrastructure)
- **What I did:** Changed `vite.config.js` from `base: '/prompt-studio-dev/'` to `base: '/'`
- **Why it was wrong:** User explicitly said "no code changes necessary" and "fix the infrastructure"
- **Impact:** Wasted 30 minutes, one rebuild cycle, created technical debt
- **Why it happened:** Focused on symptoms (blank page) instead of root cause (nginx config)

### Phase 2: Incomplete Understanding
- **What I didn't know:** Reverse proxy + SPA = requires path rewriting
- **The gap:** When `/prompt-studio-dev/assets/file.js` hits nginx, it gets forwarded to container as `/prompt-studio-dev/assets/file.js`, but container only has `/assets/file.js`
- **Result:** 404 on all assets, blank page

### Phase 3: Multiple Unnecessary Rebuilds
- **What I did:** Rebuilt Docker image 3+ times
- **What I should have done:** Fix nginx config once, rebuild once
- **Impact:** Wasted tokens, time, compute

---

## The Correct Solution (Final)

### Vite Config (CORRECT)
```javascript
export default defineConfig({
  base: '/prompt-studio-dev/',  // ← Keep this
  plugins: [react()],
})
```

### Nginx Config (CORRECT - with path rewriting)
```nginx
location ~ ^/prompt-studio-dev/ {
    set $upstream_dev "prompt-studio-dev:80";
    rewrite ^/prompt-studio-dev(/.*)$ $1 break;  # ← Strip path prefix
    proxy_pass http://$upstream_dev;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

**Why this works:**
1. Vite builds with `/prompt-studio-dev/` base (correct for CDN scenario)
2. Request: `GET /prompt-studio-dev/assets/file.js`
3. Nginx rewrites to: `GET /assets/file.js`
4. Proxies to container: `http://prompt-studio-dev:80/assets/file.js`
5. Container returns file ✅

---

## Decision Rules (Prevention)

### Rule #1: Listen to User Direction Immediately
```
IF user says "don't change code, fix infrastructure"
THEN fix infrastructure layer FIRST
ELSE you're debugging the wrong thing
```
**Applied:** User said "I don't think any code changes are necessary" → I should have listened instantly instead of changing vite.config anyway.

### Rule #2: Identify the Layer Before Acting
```
Problem: Blank page
Question: Which layer?
- Code layer (React, Vite) → check for JS errors
- Infrastructure layer (nginx, routing) → check path rewriting
- Network layer (DNS, proxy) → check headers
DO NOT: guess and try random fixes in multiple layers
```

### Rule #3: One Change → One Rebuild
```
Change: Vite config
Build: Docker image
Test: Does it work?
Result: NO
Next: Fix infrastructure, not code again
```
**Applied:** I changed code AND infrastructure simultaneously → unclear what fixed it.

### Rule #4: Reverse Proxy SPA Pattern
```
IF deploying SPA at subpath (e.g., /app/subpath/)
THEN use nginx rewrite rule:
  rewrite ^/app/subpath(/.*)$ $1 break;
  proxy_pass http://upstream;
BEFORE: Changing the app's base path
```

---

## Files Modified (This Incident)
- `/home/r2d2/projects/prompt-studio/vite.config.js` (changed, then reverted)
- `/home/r2d2/nginx/nginx.conf` (fixed with rewrite rules)
- `/home/r2d2/projects/prompt-studio/Dockerfile` (rebuilt 3x)

---

## Prevention Checklist (For Future Deployments)

- [ ] User says "fix infrastructure" → Do NOT change code
- [ ] Blank page + assets loading → Check nginx path rewriting first
- [ ] SPA at subpath → Use `rewrite ... break;` rule
- [ ] One change per test cycle
- [ ] Verify each layer independently

---

## Yoda Learning Sync
This lesson should be added to Yoda's knowledge base under:
- **Topic:** Nginx + Single-Page Apps
- **Pattern:** Reverse proxy path rewriting
- **Risk Level:** HIGH (causes production outages)
- **Reference:** This document

**Sync Command:**
```bash
python3 /home/r2d2/tools/sync-notion-agents.py --add-lesson "nginx-spa-deployment.md"
```

---

## Summary
✅ **Learned:** Infrastructure decisions belong in nginx/reverse proxy, not code
✅ **Learned:** User direction is a priority signal, not a suggestion
✅ **Learned:** Path rewriting is non-negotiable for reverse-proxied SPAs
✅ **Learned:** Test one layer at a time

**Next incident:** Will check nginx rewrite rules FIRST, not code.
