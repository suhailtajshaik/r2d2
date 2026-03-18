# Maxwell News SaaS — Architecture & Roadmap

**Vision:** Professional, personalized newspaper for each user. From general to laser-focused interests.

---

## Phase 1: Foundation (Current → 2 weeks)
**Goal:** Make Maxwell independent, multi-user ready.

### Core Services
1. **RSS Feed Engine** (`feeds_service.py`)
   - Clone awesome-rss-feeds repo for 500+ curated feeds
   - Organize by category + country
   - Fetch, parse, deduplicate
   - Support: "favorite" feeds per user

2. **Editor Service** (`editor_service.py`)
   - Maxwell's editorial rules (EDITOR.md)
   - Takes raw + user interests → produces articles
   - Quality gates: Min length, no duplicates, freshness check
   - Personalized prompts (vs global)

3. **PDF + Audio** (`render_service.py`)
   - HTML → PDF via wkhtmltopdf (current)
   - PDF → Audio via gTTS or ElevenLabs
   - Support: PDF report, audio digest, web preview

4. **Archive & Delivery** (`archive_service.py`)
   - Save to PostgreSQL (not just filesystem)
   - API for fetching user's editions
   - Email/WhatsApp/Telegram delivery
   - API: `/api/editions/{userId}/{date}.json`

### Database Schema (PostgreSQL)
```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  timezone VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
);

-- User Interests (categories + countries)
CREATE TABLE user_interests (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  category VARCHAR,  -- "Technology", "Sports", "Business", etc.
  country VARCHAR,   -- "US", "India", "UK", etc.
  priority INT,      -- 1=high, 2=medium, 3=low
  enabled BOOLEAN DEFAULT true
);

-- RSS Feeds (curated, cached from awesome-rss-feeds)
CREATE TABLE rss_feeds (
  id UUID PRIMARY KEY,
  title VARCHAR,
  url VARCHAR UNIQUE,
  category VARCHAR,
  country VARCHAR,
  last_fetched TIMESTAMP,
  status VARCHAR  -- 'active', 'dead', 'suspended'
);

-- Articles (raw from RSS before editing)
CREATE TABLE raw_articles (
  id UUID PRIMARY KEY,
  feed_id UUID REFERENCES rss_feeds(id),
  title VARCHAR,
  description TEXT,
  link VARCHAR,
  published_at TIMESTAMP,
  fetched_at TIMESTAMP DEFAULT NOW()
);

-- Edited Articles (after Maxwell processes)
CREATE TABLE articles (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  date DATE,
  section VARCHAR,    -- "Technology", "Sports", etc.
  headline VARCHAR,
  lede TEXT,
  body TEXT,
  kicker TEXT,
  read_time VARCHAR,
  source_article_ids UUID[],  -- which raw articles this came from
  created_at TIMESTAMP DEFAULT NOW()
);

-- Editions (daily newspapers per user)
CREATE TABLE editions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  date DATE,
  articles_count INT,
  pdf_path VARCHAR,
  audio_path VARCHAR,
  published_at TIMESTAMP DEFAULT NOW()
);

-- Delivery History
CREATE TABLE deliveries (
  id UUID PRIMARY KEY,
  edition_id UUID REFERENCES editions(id),
  user_id UUID REFERENCES users(id),
  channel VARCHAR,  -- 'email', 'whatsapp', 'telegram', 'web'
  status VARCHAR,   -- 'pending', 'sent', 'failed'
  sent_at TIMESTAMP,
  error_message TEXT
);
```

### API Endpoints (Backend)
```
POST   /api/users                  # Create user
POST   /api/users/{id}/interests   # Set interests
GET    /api/editions/{userId}/{date}  # Fetch edition
GET    /api/editions/{userId}      # List user's editions
POST   /api/editions/generate      # Trigger generation (for userId)
GET    /api/feeds                  # List all available feeds
POST   /api/settings               # User preferences
```

---

## Phase 2: Personalization (Weeks 3-4)
**Goal:** User profiles, interest selection, personalized editions.

### Features
1. **Interest Manager UI**
   - Choose categories: Technology, Sports, Business, Politics, Health, etc.
   - Choose countries: US, India, UK, Australia, etc.
   - Set priority: Featured, Regular, Optional
   - Preview: "Your edition will include X articles from Y feeds"

2. **Smart Filtering**
   - User interests → RSS feeds mapping
   - Fetch only relevant feeds for user
   - Maxwell gets interest context in prompt
   - Example: "This user cares about AI, Startups, India. Prioritize accordingly."

3. **Personalized Editing**
   - Maxwell adapts tone based on user (e.g., technical for engineers, general for executives)
   - Sections ordered by user interest (featured first)
   - Length adapts to user preference (5 min vs 15 min read)

4. **User Dashboard**
   - Settings: Name, email, delivery time, timezone
   - Interests: Add/remove categories and countries
   - History: View past editions
   - Preferences: PDF/audio length, delivery method, frequency

---

## Phase 3: Scale (Weeks 5+)
**Goal:** Multi-user SaaS, monetization ready.

### Features
1. **Subscription Tiers**
   - Free: 1 edition/week, limited interests (5 max)
   - Pro: Daily edition, unlimited interests, premium sections, audio
   - Premium: Custom feed sources, advanced filters, API access

2. **Delivery Channels**
   - Email: HTML + PDF attachment
   - WhatsApp: Text + PDF link
   - Telegram: Channel subscription
   - Mobile app: iOS/Android via React Native

3. **Advanced Personalization**
   - ML: Track which sections user reads → recommend more
   - A/B testing: Different headline styles, article lengths
   - Trending: What's hot in user's interest areas
   - Recommendations: "Articles similar to ones you read"

4. **Monetization**
   - Freemium model (current free, premium features)
   - Sponsorships: Curated ads in specific sections
   - API access for enterprise (B2B newspapers)
   - White-label: Rebrand for news organizations

---

## Architecture: Maxwell SaaS

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│     (React/Next.js Dashboard + Email/WhatsApp)          │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   Backend API                           │
│  (Node.js/Python FastAPI - /api/users, /api/editions)   │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │              │              │
        ▼              ▼              ▼              ▼
   ┌────────┐  ┌────────────┐  ┌─────────┐  ┌──────────┐
   │ Feeds  │  │  Maxwell   │  │ Render  │  │ Archive  │
   │Service │  │   Editor   │  │Service  │  │Service   │
   └────────┘  └────────────┘  └─────────┘  └──────────┘
        │              │              │              │
        └──────────────┼──────────────┴──────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────────────────────────────────┐
   │       PostgreSQL Database           │
   │ (users, interests, feeds, articles) │
   └─────────────────────────────────────┘
        │
        └─────────┬─────────┬─────────┬──────────┐
                  │         │         │          │
              Email     WhatsApp   Telegram    Mobile
```

---

## Tech Stack

### Backend
- **API Server:** FastAPI (Python) or Node.js/Express
- **Database:** PostgreSQL
- **Job Queue:** Celery (Python) or Bull (Node.js) for daily generation
- **Cache:** Redis for feed cache + user session
- **Search:** Elasticsearch for article search (future)

### Frontend
- **Dashboard:** Next.js + React (TypeScript)
- **Styling:** Tailwind CSS (matches Suhail's style)
- **Email:** React Email (HTML emails)
- **Mobile:** React Native Expo (iOS/Android)

### Services
- **PDF:** wkhtmltopdf
- **Audio:** gTTS (free) or ElevenLabs (premium)
- **Email delivery:** SendGrid or AWS SES
- **WhatsApp:** Twilio or WhatsApp Business API
- **Storage:** S3 or local filesystem + CDN

---

## Immediate Next Steps

### Week 1
1. ✅ Fork/clone awesome-rss-feeds repo
2. Parse OPML files → feeds table in PostgreSQL
3. Build `feeds_service.py` with user interest filtering
4. Set up PostgreSQL + schema

### Week 2
1. Refactor Maxwell: Make it take user interests + profile
2. Build editor personalization logic
3. API: `/api/editions/generate` endpoint
4. Test: Generate 3 custom editions for different users

### Week 3
1. Build interest manager UI (simple Next.js page)
2. User dashboard (view/edit profile)
3. Integration: User selects interests → generation respects choices
4. Delivery setup

---

## Inspiration & Competitors
- **Flipboard:** Personalized magazine app
- **Plenary:** RSS aggregator with local news (the awesome-rss-feeds owner)
- **Substack:** Independent publications
- **Morning Brew, The Hustle:** Premium daily newsletters
- **News360:** AI-personalized news

---

## Success Metrics
- Users can generate custom newspaper in <2 min
- 80% of delivered articles read by user
- Retention: 50%+ weekly active users
- NPS: >40 (net promoter score)
- Revenue: $1K MRR by month 3

---

## Open Questions for Suhail
1. Paid or freemium first?
2. Target users: Individuals or enterprises?
3. Priority: Web first or mobile first?
4. Geographic focus: Global or India-centric?
5. Content moderation: Any restrictions or policies?
