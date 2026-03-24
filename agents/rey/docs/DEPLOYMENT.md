# Rey Deployment Guide

## Quick Start

### Install Dependencies
```bash
pip install pyyaml
```

### First Run — Teach Brand
```bash
cd /home/r2d2/brain/agents/rey
python3 src/rey.py --teach-brand
```

This creates `.impeccable.md` and `brand-preferences.json`.

### Manual Audit
```bash
# Single project
python3 src/rey.py --audit SellBridge

# All critical projects
python3 src/rey.py --audit-all
```

## Cron Setup

Add to OpenClaw cron:

```bash
# Weekly design audit (Mondays 4 PM EST)
openclaw cron add \
  --name "r2d2:rey-design-audit" \
  --schedule "0 16 * * 1" \
  --task "python3 /home/r2d2/brain/agents/rey/src/rey.py --audit-all"

# Monthly deep audit
openclaw cron add \
  --name "r2d2:rey-deep-audit" \
  --schedule "0 16 1 * *" \
  --task "python3 /home/r2d2/brain/agents/rey/src/rey.py --audit-all && notify Suhail"
```

## Notion Integration

Rey logs audits to Notion. Configure in `config/rey.config.yaml`:

```yaml
reporting:
  notion:
    enabled: true
    database: "Session Log"
    section: "Design Audits"
```

## Commands

### Audit Single Project
```bash
python3 src/rey.py --audit SellBridge
```

Output:
```
🎨 Rey — Auditing SellBridge...
   Path: /home/r2d2/projects/sellbridge-v2

✅ SellBridge
   Status: PASS
   Violations: 0
   Severity: none
```

### Audit All
```bash
python3 src/rey.py --audit-all
```

Audits all critical projects in sequence.

### Teach Brand
```bash
python3 src/rey.py --teach-brand
```

Interactive session to establish brand guidelines.

## Configuration

Edit `config/rey.config.yaml` to:
- Add/remove projects to monitor
- Adjust brand guidelines
- Enable/disable checks
- Customize anti-patterns

## Architecture

```
Rey
├── Config Loader → rey.config.yaml
├── Brand Preferences → memory/brand-preferences.json
├── Learnings → memory/learned-anti-patterns.json
├── Audit Engine
│   ├── Typography Check
│   ├── Color Check
│   ├── Layout Check
│   ├── Responsive Check
│   └── Anti-Pattern Check
└── Reporting
    ├── Console Output
    ├── Notion Logging
    └── Audit History
```

## Integration with Other Agents

- **Guardian:** Rey audits design, Guardian monitors infrastructure. No conflict.
- **Maxwell:** Rey could audit Maxwell's news UI, suggest design improvements.
- **3PO:** Rey could review Claude Code output for design compliance.
- **Yoda:** Rey learns design preferences over time (similar pattern to Yoda's learning).

## Troubleshooting

**Config not loading?**
```bash
python3 -c "import yaml; yaml.safe_load(open('config/rey.config.yaml'))"
```

**Projects not found?**
Check paths in `config/rey.config.yaml` — must be absolute paths.

**No audit results?**
Ensure projects have CSS/component files. Rey uses grep patterns.

## Next Steps

1. Run `--teach-brand` to establish preferences
2. Test with `--audit SellBridge`
3. Add cron job for weekly audits
4. Monitor Notion logs for design drift
5. Iterate on anti-patterns as Rey learns
