# Phase 1: Maxwell SaaS Independence — Task List

**Timeline:** 2 weeks
**Owner:** R2D2 + 3PO + Yoda review
**Goal:** Maxwell ready for multiple users with customizable interests

---

## Task 1: RSS Feeds Repository Setup
**Status:** NOT STARTED
**Assignee:** 3PO

### Subtasks
- [ ] Clone plenaryapp/awesome-rss-feeds to `/home/r2d2/projects/maxwell-feeds/`
- [ ] Parse all OPML files (countries + categories)
- [ ] Extract ~500 RSS feeds into JSON format:
  ```json
  {
    "id": "feed-001",
    "title": "BBC World",
    "url": "https://...",
    "category": "World News",
    "country": "UK",
    "type": "general"
  }
  ```
- [ ] Upload feeds JSON to PostgreSQL `rss_feeds` table
- [ ] Add feed health check (ping URLs, categorize dead feeds)
- [ ] Create `/api/feeds` endpoint to list feeds by category/country

---

## Task 2: PostgreSQL Database Setup
**Status:** NOT STARTED
**Assignee:** 3PO (with Yoda review)

### Subtasks
- [ ] Create PostgreSQL database: `maxwell_saas`
- [ ] Create all tables (see schema in DESIGN.md):
  - users, user_interests, rss_feeds, raw_articles, articles, editions, deliveries
- [ ] Create indexes: user_id, date, category, country
- [ ] Write migration scripts (for future DB updates)
- [ ] Seed test data (3 test users with different interests)

---

## Task 3: Feeds Service (`feeds_service.py`)
**Status:** NOT STARTED
**Assignee:** 3PO

### Subtasks
- [ ] Create class: `FeedsService`
  - Input: user interests (categories + countries)
  - Output: List of 20-30 relevant RSS feeds
  - Method: `get_feeds_for_user(user_id)`

- [ ] Implement feed fetching:
  - Parallel fetch (max 10 concurrent, respect rate limits)
  - Parse XML, extract title/description/link/date
  - Deduplicate (same URL appears in multiple feeds)
  - Filter by freshness (< 48h old)

- [ ] Error handling:
  - Dead feeds (mark as inactive after 3 failures)
  - Timeouts (set 15s max per feed)
  - Malformed XML (skip, log error)

- [ ] Caching:
  - Redis cache: Feed content valid for 4h
  - Invalidate on manual refresh

---

## Task 4: Refactor Maxwell — User-Aware Edition
**Status:** PARTIAL (current works for single daily edition)
**Assignee:** 3PO

### Current State
- `maxwell.py` fetches fixed 6 RSS sources
- Produces single JSON with 6 sections
- Runs via cron daily

### Changes Needed
- [ ] Accept user interest context in prompt
  ```python
  def generate_edition(user_id, date):
      user = get_user(user_id)
      interests = get_user_interests(user_id)
      feeds = FeedsService.get_feeds_for_user(user_id)
      raw_articles = fetch_articles(feeds)
      
      # NEW: Pass user interests to Claude
      editor_prompt = EDITOR.md + "\nUser interests: " + str(interests)
      articles = run_maxwell(raw_articles, editor_prompt)
      return articles
  ```

- [ ] Add personalization to EDITOR.md
  - Mention user's interests
  - Suggest section ordering
  - Adapt tone (technical vs general)

- [ ] Create `/api/editions/generate` endpoint
  - Input: `{user_id, date}`
  - Output: Generates edition, saves to DB
  - Async job (use Celery)

- [ ] Store in articles table (not just JSON files)

---

## Task 5: User & Interests API
**Status:** NOT STARTED
**Assignee:** 3PO

### Endpoints to Build
```
POST   /api/users
       Input: {email, name, timezone}
       Output: {user_id, created_at}

GET    /api/users/{id}
       Output: {id, email, name, timezone, interests: [...]}

POST   /api/users/{id}/interests
       Input: [{category: "Technology", priority: 1}, ...]
       Output: Updated interests

GET    /api/feeds?category=Technology&country=US
       Output: [{id, title, url, ...}, ...]

POST   /api/editions/generate
       Input: {user_id, date}
       Output: {edition_id, articles_count, status}
       (Async job)

GET    /api/editions/{userId}/{date}
       Output: {articles: [...], generated_at, ...}

GET    /api/editions/{userId}?limit=7
       Output: [{date, articles_count, ...}, ...]
```

---

## Task 6: Test & Validate
**Status:** NOT STARTED
**Assignee:** 3PO + Yoda

### Test Cases
- [ ] Create 3 test users (engineer, executive, news junkie)
- [ ] Set different interests for each
- [ ] Generate custom editions for each
- [ ] Verify:
  - Different feeds selected per user ✓
  - Different articles generated per user ✓
  - Section order matches interests ✓
  - Quality: No duplicates, length appropriate ✓

### Code Review (Yoda)
- [ ] Security: API inputs sanitized ✓
- [ ] Database: SQL injection prevented ✓
- [ ] Performance: Feed fetching <30s ✓
- [ ] Error handling: Graceful degradation ✓
- [ ] API design: RESTful, clear responses ✓

---

## Task 7: Documentation
**Status:** NOT STARTED
**Assignee:** R2D2

### Docs to Write
- [ ] API reference (endpoints, examples, errors)
- [ ] Developer setup (PostgreSQL, Python, dependencies)
- [ ] Architecture diagram
- [ ] Feed categories/countries reference
- [ ] Deployment guide (Docker + systemd)

---

## Blockers / Decisions
- [ ] Database host: Local PostgreSQL or cloud (RDS)?
- [ ] Job queue: Celery + RabbitMQ or simple Cron?
- [ ] Email delivery: SendGrid or AWS SES?
- [ ] Storage: Filesystem or S3?

---

## Success Criteria
- ✅ 3 test users generate custom editions independently
- ✅ Different feeds + articles per user interest
- ✅ API responds in < 2s
- ✅ No errors in logs (Yoda review passed)
- ✅ 90% feed fetch success rate
- ✅ Database has 500+ feeds indexed
- ✅ Documentation complete

---

## Timeline
- **Days 1-3:** Tasks 1-2 (feeds repo + DB setup)
- **Days 4-7:** Tasks 3-4 (services + API)
- **Days 8-10:** Task 5 (user endpoints)
- **Days 11-12:** Task 6 (testing + Yoda review)
- **Days 13-14:** Task 7 (docs + polish)
