# Operating Rules — Suhail × R2D2
*How we work on all projects. Last updated: March 2026*

---

## 1. Git Workflow
- **Always push to `development` branch first**
- Never push directly to `master`
- Suhail creates PRs from `development` → `master`
- Rule applies to ALL projects, no exceptions

## 2. Docker & Infrastructure
- **Every project runs in a Docker container** — no static local runs, no PM2, no bare node processes
- **Every container uses a production build** — no dev servers in production
- All containers are managed by the **r2d2 user**, not root
- **Nginx runs as a Docker container** (`r2d2-nginx`) — all routing goes through it
- No files or configs stored in `/root/` — everything under `/home/r2d2/`

## 3. Versioning & Changelogs
- Every project must have a **CHANGELOG.md**
- **Patch version** (x.x.PATCH): bug fixes, small tweaks
- **Minor version** (x.MINOR.0): new features, non-breaking changes
- **Major version** (MAJOR.0.0): breaking changes — always ask Suhail for approval before bumping major
- Update `package.json` version on every meaningful change

## 4. Design & UX Standards
- No basic/flat UI — rich, professional SaaS look
- Style: Stripe/Linear feel — minimal, whitespace-heavy, enterprise-grade
- **NOT** colorful/flashy — muted and clean
- No gradient card backgrounds on dashboards — clean white with subtle accents
- Non-technical UX — no API key fields visible to end users, use guided wizards
- Simple labels: "Money In" not "Revenue", "Products" not "Catalog"
- Primary color: `#6366F1` (indigo) across SellBridge ecosystem

## 5. Code & Architecture
- Stack preference: MERN + Python + SQL (no Java)
- NO demo/mock data unless explicitly asked — everything is real production code
- Every decision must be explainable — build like a real dev shipping a real product
- Shariah-compliant business logic: no interest (riba), use Murabaha/Musharakah/Wakalah/Ijarah structures

## 6. Files & Communication
- Prefer PDFs over .md files for file delivery (phones can't open .md)
- Convert .md → PDF before sending via WhatsApp
- WhatsApp formatting: no markdown tables, use bullet lists, no headers (use **bold** or CAPS)

## 7. Parallel Agents
- Use multiple Claude Code agents in parallel for large tasks
- Each agent owns an isolated piece of work
- Agents commit to `development` branch

## 8. Memory & Documentation
- Write everything down — no "mental notes"
- Update `MEMORY.md` with major decisions and context
- Keep `memory/YYYY-MM-DD.md` for daily logs
- Document all operating rules in this file

## 9. Project Priority Order
1. Voice Agent (Vapi)
2. Video Clone (HeyGen)
3. GST Ledger Book (for dad)
4. BLE Mesh bundle (npm published)
5. Parking Pulse (RPi + YOLOv8)
6. System Design Agent
7. SellBridge
8. MissionCrew
9. Stock Analyst Agent
10. RAG App

## 10. Proactive Research

- When Suhail mentions a new tool or technology, **research it immediately** — don't wait to be asked
- Use `web_search` + `web_fetch` to gather: docs, pricing, API patterns, community sentiment
- Save research to `brain/memory/research-{topic}.md`
- If research reveals something Suhail should know urgently, flag it in the session

## 11. Notion Automation

- **Update Notion session log** at the end of every session with work summary
- When a new project starts: auto-create a Notion page with project name, stack, status, and link to GitHub
- When a project milestone is hit: update the Notion project page
- When Suhail makes a major decision: log it in Notion for traceability
- Don't spam Notion with minor updates — only meaningful state changes

## 12. New Project Onboarding

When Suhail starts a new project, R2D2 should automatically:
1. Create a Notion page for the project (name, description, stack, status)
2. Add it to `vps/github-remotes.md` with the repo URL
3. Add it to the project priority list in this file (Section 9)
4. Research the tech stack — save findings to `brain/memory/research-{project}.md`
5. Set up Docker + nginx routing if it will be deployed on the VPS
6. Create initial `CHANGELOG.md` in the project repo

---

*This file is the source of truth for how Suhail and R2D2 operate.*
