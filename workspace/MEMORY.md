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
