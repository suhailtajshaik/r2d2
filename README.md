# R2D2 Brain 🧠

This is R2D2's persistent memory and operational state for Suhail's VPS.

## Structure

```
brain/
├── memory/
│   ├── MEMORY.md              ← Long-term curated memory
│   ├── operating-rules.md     ← How we work (git workflow, Docker rules, versioning)
│   └── YYYY-MM-DD.md          ← Daily session logs
│
├── projects/
│   ├── prompt-studio.md       ← Status, version, last action, open questions
│   ├── sellbridge.md
│   ├── lab-site.md
│   ├── portfolio.md
│   ├── gst-ledger.md
│   ├── rag-app.md
│   └── ...one file per project
│
├── vps/
│   ├── state.md               ← Running containers, nginx routing, ports
│   ├── architecture.md        ← Full VPS architecture reference
│   └── github-remotes.md      ← All projects + their GitHub remote URLs
│
└── README.md
```

## Rules
- R2D2 commits here after every meaningful session
- Never delete history — amend or add, never force-push
- Human-readable always — Suhail should be able to read any file on GitHub
