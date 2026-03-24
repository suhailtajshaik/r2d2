# Rey — Quick Start

**Rey** is your design quality agent. She audits design consistency across all your SaaS projects.

## First-Time Setup (2 min)

```bash
cd /home/r2d2/brain/agents/rey

# 1. Teach Rey your brand preferences
python3 src/rey.py --teach-brand

# 2. Test on a project
python3 src/rey.py --audit SellBridge

# 3. Audit everything
python3 src/rey.py --audit-all
```

## What Rey Does

✅ **Audits design** across all your projects  
✅ **Enforces anti-patterns** from Impeccable skill  
✅ **Tracks design consistency** (colors, typography, layout)  
✅ **Learns your preferences** over time  
✅ **Silent by default** — only alerts on violations  

## Projects Rey Monitors

- SellBridge (weekly)
- Maxwell News SaaS (weekly)
- Prompt Studio (biweekly)
- Portfolio (monthly)
- Lab Site (monthly)
- News Site (weekly)

## Commands

| Command | Purpose |
|---------|---------|
| `--audit SellBridge` | Audit single project |
| `--audit-all` | Audit all critical projects |
| `--teach-brand` | Set up brand preferences |
| `--config path/to/config.yaml` | Use custom config |

## Configuration

Edit `config/rey.config.yaml` to:
- Add/remove projects
- Adjust brand colors & fonts
- Change audit frequency
- Customize anti-patterns

## Brand Guidelines (Default)

- **Aesthetic:** Stripe/Linear inspired
- **Primary Color:** #6366F1 (Indigo)
- **Fonts:** Not Inter, not Roboto
- **Spacing:** Generous whitespace
- **Avoid:** Nested cards, purple gradients, AI-slop patterns

## Cron Scheduling

Add to OpenClaw:

```bash
openclaw cron add \
  --name "r2d2:rey-weekly-audit" \
  --schedule "0 16 * * 1" \
  --task "python3 /home/r2d2/brain/agents/rey/src/rey.py --audit-all"
```

## Output

```
🎨 Rey — Auditing SellBridge...
   Path: /home/r2d2/projects/sellbridge-v2

✅ SellBridge
   Status: PASS
   Violations: 0
   Severity: none
```

## Memory

Rey remembers:
- Brand preferences (in `memory/brand-preferences.json`)
- Anti-pattern learnings (in `memory/learned-anti-patterns.json`)
- Audit history (in `memory/audit-history.json`)

## Integration

Works with:
- **Impeccable** — 21 design commands
- **21st.dev** — Component library
- **ui-ux-pro-max** — Design guidelines
- **Guardian** — Infrastructure monitoring (no conflict)
- **3PO** — Reviews Claude Code output for design

## What's Next?

1. ✅ Run `--teach-brand` to set preferences
2. ✅ Test with `--audit SellBridge`
3. ✅ Add cron job for weekly audits
4. ✅ Monitor Notion logs for design metrics
5. ✅ Let Rey learn your design patterns

---

**Questions?** Check `docs/DEPLOYMENT.md` for detailed setup.
