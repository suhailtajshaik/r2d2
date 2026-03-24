# Rey — Design Agent

**Purpose:** Monitor, audit, and improve design consistency across all Suhail's SaaS projects.

**Responsibilities:**
- Audit UI/UX across SellBridge, Maxwell, Prompt Studio, portfolio, lab
- Enforce brand guidelines (Stripe/Linear aesthetic, Impeccable anti-patterns)
- Run Impeccable design commands (`/audit`, `/polish`, `/typeset`, `/arrange`)
- Track design drift and suggest improvements
- Self-evolve design patterns based on feedback
- Integration with Notion for design quality metrics

**Architecture:**
```
Rey Agent
├── Design Auditor (Impeccable + frontend-design skill)
├── Brand Enforcer (color, typography, layout rules)
├── Pattern Tracker (learns design preferences)
└── Cron Monitor (scheduled design checks)
```

**Key Features:**
- Silent by default (only alerts on violations)
- Learns from corrections (improves over sessions)
- Multi-project awareness (tracks consistency across apps)
- Notion integration (logs design audits to Session Log)
- Skill-based (uses Impeccable 21 commands)

**Deployment:**
```bash
# Manual trigger
python3 /home/r2d2/brain/agents/rey/src/rey.py --audit SellBridge

# Scheduled (cron)
# Daily design audit at 4 PM EST
r2d2:rey-design-audit

# Via OpenClaw
openclaw agent spawn rey
```

**Status:** 🚧 In Development

---

**Agent Details:**
- **Framework:** Python + LLM (Claude/OpenAI)
- **Skills:** Impeccable (21 commands), frontend-design, 21st.dev reference
- **Monitoring:** SellBridge, Maxwell, Prompt Studio, portfolio, lab, news-site
- **Output:** Design reports, Notion logs, improvement suggestions
- **Learning:** Brand preferences, anti-pattern avoidance, style evolution
