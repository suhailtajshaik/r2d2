# Maxwell News SaaS 📰

**Professional personalized newspaper platform. Every user, their own edition.**

---

## What is Maxwell?

Maxwell takes news from 500+ RSS feeds across 30+ countries and 50+ categories, then uses AI to create a personalized newspaper for each user based on their interests.

**Today:** Suhail gets "The Headlines Today" (one daily newspaper)
**Tomorrow:** Every user gets THEIR newspaper, tailored to THEIR interests

---

## Example Flow

1. **User profile:** Suhail (engineer, India-focused)
   ```json
   interests: [
     {category: "Technology", priority: "High"},
     {category: "Business", priority: "Medium"},
     {country: "India", priority: "High"}
   ]
   ```

2. **Maxwell generates edition:**
   - Fetches relevant feeds: BBC Tech + Hacker News + Times of India + NDTV
   - ~40 raw articles
   - Claude (Maxwell) edits them into clean, publication-ready pieces
   - 8-12 curated articles tailored to Suhail

3. **Delivery:**
   - PDF: Email + WhatsApp
   - Audio: Digest read aloud
   - Web: View in dashboard
   - Mobile: iOS/Android app

---

## Architecture

```
User Dashboard (Next.js)
        ↓
API (FastAPI) — /api/users, /api/interests, /api/editions
        ↓
┌─────────────────────────────────────────┐
│  Feeds Service  │  Maxwell Editor │ Renderer
│  (RSS fetcher)  │  (Claude)      │ (PDF/Audio)
└─────────────────────────────────────────┘
        ↓
PostgreSQL Database
┌─────────────────────────────────────────┐
│ users | user_interests | rss_feeds      │
│ articles | editions | deliveries        │
└─────────────────────────────────────────┘
        ↓
Delivery (Email, WhatsApp, Telegram)
```

---

## Phase 1: Foundation (Current — 2 weeks)
Make Maxwell independent, ready for multiple users.

### Key Tasks
1. Clone awesome-rss-feeds repo (500+ feeds, 30+ countries)
2. Set up PostgreSQL (users, interests, feeds, articles tables)
3. Build feeds service (filter feeds by user interests)
4. Refactor Maxwell to accept user profiles
5. Build API endpoints for users + interest management
6. Test: 3 users, 3 different custom editions

**Status:** Planning phase
**Docs:** See PHASE_1_TASKS.md

---

## Phase 2: Personalization (2 weeks)
User dashboard, interest selection, personalized editions.

- User profile + settings
- Interest manager (pick categories + countries)
- Custom edition preview before generation
- Delivery preferences (time, channel, format)

---

## Phase 3: Scale (Ongoing)
Subscription tiers, mobile app, monetization.

- Freemium model (1 edition/week free, daily for Pro)
- Mobile apps (iOS/Android)
- Advanced personalization (ML, recommendations)
- Sponsorships + API access for B2B

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, React, Tailwind CSS, TypeScript |
| **Backend** | FastAPI (Python) or Node.js/Express |
| **Database** | PostgreSQL |
| **Job Queue** | Celery (Python) or Bull (Node.js) |
| **Cache** | Redis |
| **Storage** | S3 or local + CDN |
| **Email** | SendGrid or AWS SES |
| **PDF** | wkhtmltopdf |
| **Audio** | gTTS (free) or ElevenLabs (premium) |
| **Delivery** | Twilio (SMS/WhatsApp), Telegram Bot API |

---

## Key Files

- **DESIGN.md** — Full architecture, database schema, API spec, phase roadmap
- **PHASE_1_TASKS.md** — 2-week sprint, task breakdown, success criteria
- **Current maxwell.py** — Will be refactored for multi-user in Phase 1

---

## Success Metrics

- Users generate custom newspaper in < 2 minutes
- 80% of articles read by user
- 50%+ weekly active users (retention)
- 100+ users by end of Q2
- $1K MRR by month 3 (if paid)

---

## Open Questions for Suhail

1. **Business model:** Freemium, paid-only, or ad-supported?
2. **Target:** Individuals or enterprises?
3. **Priority:** Web or mobile first?
4. **Geography:** Global or India-focused?
5. **Launch target:** When do you want Phase 1 done?

---

## How to Get Started

**For Suhail (Product Owner):**
1. Review DESIGN.md (10 min read)
2. Answer open questions above
3. Prioritize features vs timeline
4. Approve Phase 1 tasks

**For 3PO (Developer):**
1. Read PHASE_1_TASKS.md
2. Start with Task 1 (feeds repo)
3. Task 2 (PostgreSQL setup)
4. Keep Yoda updated for code review

**For Yoda (Reviewer):**
1. Review code against best practices
2. Check security (SQL injection, API validation)
3. Performance (feed fetching, DB queries)
4. Provide feedback before each phase

---

## Timeline
- **Week 1:** Feeds repo + DB setup (Tasks 1-2)
- **Week 2:** Services + API (Tasks 3-5)
- **Week 3:** Testing + Yoda review (Task 6)
- **Week 4:** Documentation + deployment (Task 7)
- **Phase 2:** User dashboard + personalization
- **Phase 3:** Monetization + scale

---

## Questions?

Ask R2D2 or consult Yoda for architecture wisdom.
