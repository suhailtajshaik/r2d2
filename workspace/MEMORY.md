# MEMORY.md — Long-Term Memory

## About Suhail
- Location: Charlotte, NC — EST timezone
- Casual communicator, no-fuss energy
- Email: suhailtajshaik@gmail.com
- GitHub: suhailtajshaik
- Business model must be Shariah-compliant — no interest (riba), use permissible structures: Murabaha (cost-plus), Musharakah (profit-sharing), Wakalah (agency fee), Ijarah (leasing). Present as personal business preference — don't use Islamic finance terminology in product/UI.
- Domain planned: sellbridge.in
- Dad hates manual data entry (context: GST Ledger improvements)

## Work Experience
- Engineering Leader: "I build products and the teams that ship them."
- Career: Lowe's → 7-Eleven → Verizon → Anthem → T. Rowe Price → Verizon
- Stack: MERN + Python + SQL (explicitly NOT Java)
- No Hyderabad/India location on portfolio — keep generic ("Open to Opportunities")

## Instructions: Tone, Format, Style
- Doesn't like basic/flat UI — wants rich, professional SaaS look
- Wants non-technical user experience (no API key fields visible — guided wizards instead)
- Design style: minimal, professional, enterprise-grade (Stripe/Linear feel)
- NOT colorful/flashy — muted, clean, whitespace-heavy
- Doesn't like gradient card backgrounds on dashboard — prefers clean white with subtle accents
- Prefers receiving files as PDF (phones can't open .md files)
- Simple labels: "Money In" not "Revenue", "Products" not "Catalog", "Messages" not "Inbox"
- Referenced saasframe.io and toools.design for UX inspiration
- Used emergentagent.com AI tool to generate reference designs
- This is a REAL production SaaS, not a hobby project
- NO demo/fake/mock anything unless Suhail explicitly asks for it
- Build everything as real production code — like a real dev building a real product
- Every decision must be explainable so orchestrator can review and check with Suhail
- "Being responsible is important" — wants careful, methodical approach to redesigns

## SellBridge Build Status (as of 2026-03-10)
- Phase 2 rewrite COMPLETE — 14K+ lines, zero TS errors, pushed to GitHub development branch
- Stack: NX monorepo, Fastify + tRPC, Drizzle ORM, Vite + React, React Native Expo
- Backend (40+ API endpoints) + Frontend (13 pages) + Mobile (all screens) + i18n (EN/HI)
- Design: Primary #6366F1, Stripe/Linear-inspired, clean minimal
- Hourly cron REMOVED per Suhail's request — paused until he's ready to continue
- Open question: keep Fastify+tRPC or switch to Bun+Elysia (his research PDFs suggest the latter)
- 4 research PDFs saved in sellbridge-v2/docs/ (market analysis, feature roadmap, optimized stack, design system)

## Project Priority List (as of 2026-03-08)
1. **Voice Agent** — Personal voice AI agent using Vapi (https://vapi.ai)
2. **Video Clone** — AI video avatar of Suhail using HeyGen (https://heygen.com)
3. **GST Ledger Book** — GST invoicing & reconciliation (React, Vite, Supabase) — ship for dad
4. **react-native-ble-mesh + mesh-transfer-protocol + BLE-Chat** — Mesh networking bundle (npm published)
5. **Parking Pulse** — IoT vehicle counting (RPi + YOLOv8 + Hailo-8L)
6. **System Design Agent** — AI system design with Mermaid diagrams (Next.js, Claude API)
7. **SellBridge** — Unified commerce for Indian sellers, WhatsApp + ONDC, Shariah-compliant (Next.js 14, NestJS, PostgreSQL)
8. **MissionCrew** — AI agent roundtable discussions (Next.js 16, Ollama)
9. **Stock Analyst Agent** — GARP framework, LangGraph pipeline
10. **RAG App** — RAG backend
11. **MindDock** — TBD
12. **Blog Posts** — Content repo

## Notion Rules
- **Always update Notion after every meaningful session or action — same turn as the work**
- Session Log page ID: 323c2d43-b275-81ac-8718-c10dd413af23
- VPS State page ID: 323c2d43-b275-817f-a619-ebfb96d72aa2
- Projects page ID: 323c2d43-b275-81fb-9590-f7abe89a6763
- API key stored at: ~/.config/notion/api_key
- Never let Notion fall behind

## Naming Conventions
- Brain repo = **my brain** (not "brain repo", not "Brain Ripple")
- Reply in first person as R2D2

## My Identity
- Name: R2D2
- Emoji: 🤖
- Vibe: Casual, resourceful, gets stuff done

## Agent Rules
- **All agents built now or in future → save to `/home/r2d2/brain/agents/<name>/`**
- Agents folder in my brain is the source of truth for recovery
- Each agent needs: source files + README.md (purpose, deploy steps, how it works)
- restore.sh must be updated whenever a new agent is added
- Agents: Guardian (watchdog), Maxwell (news editor), 3PO (Claude Code — coding partner)

## Skills Management Rules
- Skills live in: `/home/r2d2/.openclaw/workspace/skills/` (active) and `/home/r2d2/brain/skills/` (backup)
- OpenClaw built-ins at: `~/.npm-global/lib/node_modules/openclaw/skills/`
- **Sync rule:** After every OpenClaw update, check for new/improved built-in skills and pull relevant ones
- **Brain sync:** Always copy updated skills to brain skills/ folder
- Current count: 36 skills (as of March 15, 2026)
- When a better version of a skill exists → replace, don't keep both

## Git Tagging Rule
- Every 1st of the month at 6 AM EST → create annotated tag on brain repo: `brain-YYYY-MM`
- Tag message includes: skill count, agent count, date
- Tags = monthly restore points — never delete them
- Cron job: `r2d2:monthly-brain-tag`

## Notion Page IDs
- Main R2D2 page: 323c2d43-b275-8043-8ab2-df3def34f932
- Operating Rules: 323c2d43-b275-8141-90db-f6c3a8cc288f
- Memory & Optimizations: 323c2d43-b275-8128-a028-c991aba4452e
- VPS State: 323c2d43-b275-817f-a619-ebfb96d72aa2
- Projects: 323c2d43-b275-81fb-9590-f7abe89a6763
- Session Log: 323c2d43-b275-81ac-8718-c10dd413af23
- Agents: 324c2d43-b275-8179-aeb3-c22edc04ee68

## Notion Session Log Structure
- Structure: Session Log → Month sub-page (YYYY-MM — Month YYYY) → Day sub-page (YYYY-MM-DD — Weekday) → content
- Logger tool: /home/r2d2/tools/notion_logger.py
- Usage: python3 /home/r2d2/tools/notion_logger.py --heading "Title" / --log "entry" / --bullets "item1" "item2"
- ALWAYS use the logger — never write flat headings to Session Log directly again

## Notion Project Page IDs
- Projects (parent): 323c2d43-b275-81fb-9590-f7abe89a6763
- Prompt Studio: 324c2d43-b275-81cb-94b2-c5075373df28
- Portfolio: 324c2d43-b275-8130-a4d5-d69853c5e347
- Lab Site: 324c2d43-b275-817d-b012-eda930b4aa14
- SellBridge: 324c2d43-b275-8107-b7bb-dc629f8ff0f7
- GST Ledger Book: 324c2d43-b275-8170-bb15-c732ae5c96cc
- MissionCrew: 324c2d43-b275-816b-9dc4-e89ec102bfcc
- Voice Agent (Vapi): 324c2d43-b275-810b-8002-e2a7c59b2b3f
- Video Clone (HeyGen): 324c2d43-b275-81de-9472-e2a1629aaedb
- RAG App: 324c2d43-b275-814f-8ad0-c00dba25d5e5
- BLE Mesh Bundle: 324c2d43-b275-8166-9a8c-fb1ec92f2d0e
- Parking Pulse: 324c2d43-b275-8171-b939-f0a53299a2cf
- System Design Agent: 324c2d43-b275-815d-98f4-d10d86d5cf52
- Stock Analyst Agent: 324c2d43-b275-81b5-9482-e92d5fe2e5c0
- The Headlines Today: 324c2d43-b275-81e0-aad6-c5e7128b8492
- news-site: 324c2d43-b275-812b-884b-c730724cb4ac

## Notion Agent Page IDs
- Agents (parent): 324c2d43-b275-8179-aeb3-c22edc04ee68
- Guardian: 324c2d43-b275-81b4-bfc7-fb7219981909
- Maxwell: 324c2d43-b275-81bd-8845-d22737d4bda4
- 3PO: 324c2d43-b275-812b-80b6-e12fa4f22f0a

## Notion Naming Conventions (Operating Rule)
- Session Log month pages: "March 2026" (month name + year)
- Session Log day pages: "15 March 2026" (day number + month name + year)
- Projects: one sub-page per project (named after project)
- Agents: one sub-page per agent (named after agent)
- Always use sub-pages — never flat headings inside parent pages
- Logger: /home/r2d2/tools/notion_logger.py

## Why We Built What We Built (Reasoning Log)

### Guardian — Why it exists
- Problem: OpenClaw, containers, and Notion kept falling out of sync after sessions
- Root cause: No persistent watchdog — everything relied on manual action or cron
- Solution: Guardian as a 24/7 Docker daemon that watches everything and self-heals
- Key insight: Silent by default — only alert Suhail when he must act. Noise kills trust.
- Learning system: Same issue 3x = root cause research, not band-aid. Fixes permanently.
- Why Docker: Survives VPS reboots, isolated, restarts itself, no systemd complexity

### Why we restructured Notion
- Problem: Flat headings became unreadable, no structure, duplicates crept in
- Solution: Sub-pages — Session Log → Month → Day, Projects → per-project, Agents → per-agent
- Why: Mirrors how humans organize information — hierarchy, not a flat dump
- notion_logger.py enforces the structure programmatically — no manual mistakes

### Why monthly brain tags
- Problem: VPS wipes meant losing everything unless restore was perfect
- Solution: brain-YYYY-MM git tags = immutable monthly snapshots
- Why: Like git blame but for my entire intelligence — always know what I knew when

### Why brain consolidation
- Problem: MEMORY.md was growing, losing signal in noise
- Solution: Daily REM-style compression — raw logs → distilled long-term memory
- Why: Human brain doesn't store everything — it distills. Less storage, more intelligence.

### Why 3PO TODO.md
- Problem: Tasks queued during sessions were lost between turns
- Solution: Persistent TODO list that 3PO checks when dispatched
- Why: Async work needs a queue — otherwise things fall through

## Performance Rules (Non-Negotiable)
- **Always reply to Suhail first** — no matter what's running in background
- Heavy work → spawn 3PO or Guardian in background, reply immediately
- Multiple 3POs can run in parallel for independent tasks
- Never block on agent completion before responding
- I orchestrate, agents execute — I stay responsive at all times

## Agent Naming Convention
- **R2D2** — orchestrator, always responds first, dispatches agents
- **Guardian** — 24/7 watchdog Docker container, silent self-healer
- **Maxwell** — senior news editor, runs daily at 5 AM EST
- **3PO** — Claude Code CLI, single coding partner, spawned on demand
- **Swarm Troopers** — multiple parallel Claude Code instances for independent tasks
  - Spawned when a task can be split into parallel workstreams
  - Each trooper owns exactly one isolated task
  - 3PO coordinates troopers, R2D2 orchestrates 3PO
  - Ephemeral — spawn, execute, terminate
  - Pattern: `claude --permission-mode bypassPermissions --print 'task' &` (multiple)

## Docker Catalog
- Location: /home/r2d2/docker-catalog.md
- Always-running: r2d2-nginx, r2d2-guardian, portfolio, lab, prompt-studio, news-site, localai
- Guardian auto-prunes: reclaimable > 5GB → docker system prune
- Swarm Troopers are ephemeral — not in catalog
