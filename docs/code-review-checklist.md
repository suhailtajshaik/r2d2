# Code Review Checklist — R2D2 Standards

Use this when reviewing code before shipping or major commits.

## Security
- [ ] No API keys hardcoded or in `.env.public`
- [ ] No secrets in frontend code or git history
- [ ] All API calls go through backend proxy (not direct browser→API)
- [ ] Sensitive data encrypted at rest & in transit
- [ ] Auth tokens not leaked in logs or network tab
- [ ] CORS headers are restrictive (not `*`)
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevention (sanitize user input)
- [ ] CSRF tokens on state-changing requests

## API Design
- [ ] API keys/secrets stored server-side only
- [ ] Rate limiting implemented (per-user, per-IP)
- [ ] Exponential backoff on 5xx errors
- [ ] Proper error handling (don't expose internals)
- [ ] Request/response logging for debugging
- [ ] Cache strategy documented (what, how long, when to invalidate)
- [ ] Timeout values set (avoid hanging requests)

## Frontend
- [ ] No direct API calls to external providers
- [ ] All external API calls proxied through backend
- [ ] Environment variables don't contain secrets
- [ ] API key input comes via wizard, not raw field
- [ ] Sensitive data not stored in localStorage
- [ ] Loading states prevent double-submit
- [ ] Error messages user-friendly (not technical)

## Backend
- [ ] Input validation on all endpoints
- [ ] Output sanitized before sending to client
- [ ] Proper HTTP status codes (not 200 for errors)
- [ ] Rate limiting per user/IP
- [ ] Request deduplication (prevent duplicate work)
- [ ] Retry logic with backoff
- [ ] Database queries optimized (no N+1)
- [ ] Monitoring/alerting for failures
- [ ] Graceful degradation on API provider outage

## Testing
- [ ] Rate limit scenarios tested
- [ ] Error paths tested (429, 500, timeout)
- [ ] Happy path tested
- [ ] Concurrent requests tested
- [ ] Large payloads tested

## Deployment
- [ ] Secrets in .env, never in code
- [ ] Environment-specific configs separated
- [ ] Rollback plan documented
- [ ] Monitoring dashboards set up
- [ ] Log aggregation configured

## Specific to Dev Tools
- [ ] No API key exposure in browser
- [ ] Backend proxy used for all LLM calls
- [ ] Retry logic + backoff implemented
- [ ] Request deduplication working
- [ ] Cache hit rates monitored

---
*Updated: March 17, 2026 — Added API architecture rule after Prompt Studio rate limit incident*
