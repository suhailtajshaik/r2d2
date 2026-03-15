# R2D2 Brain

Persistent memory, operational state, and self-improvement system for R2D2 — Suhail's personal AI assistant running on a VPS via OpenClaw.

## Structure

```
brain/
├── workspace/                  ← OpenClaw workspace files (synced both ways)
│   ├── MEMORY.md               ← Long-term curated memory
│   ├── SOUL.md                 ← R2D2's identity and principles
│   ├── USER.md                 ← Suhail's profile
│   ├── AGENTS.md               ← Session guidelines and agent behavior
│   ├── TOOLS.md                ← Tool-specific notes (PDF, WhatsApp, etc.)
│   ├── IDENTITY.md             ← Name, emoji, vibe
│   └── HEARTBEAT.md            ← Heartbeat task config
│
├── memory/                     ← Knowledge base
│   ├── MEMORY.md               ← Memory index
│   ├── operating-rules.md      ← How Suhail and R2D2 work together
│   ├── research-links.md       ← Bookmarks and research references
│   └── YYYY-MM-DD.md           ← Daily session logs
│
├── research/                   ← Self-improvement system
│   └── HOW_TO_LEARN.md         ← Patterns for web research and learning
│
├── vps/                        ← VPS infrastructure state
│   ├── state.md                ← Running containers, nginx routing, ports
│   ├── github-remotes.md       ← All projects + GitHub URLs + versions
│   ├── gitconfig-r2d2          ← Git global config
│   └── nginx-conf/             ← Full nginx config backup
│       ├── nginx.conf
│       ├── docker-compose.yml
│       └── conf.d/             ← Site configs + common includes
│
├── skills/                     ← 26 custom OpenClaw skills (backed up)
│
├── restore.sh                  ← One-command full system restore
├── sync.sh                     ← Sync workspace → brain repo → GitHub
├── RESTORE.md                  ← Detailed restore guide
├── DAILY_TASKS.md              ← Daily/weekly self-improvement checklist
└── README.md                   ← This file
```

## Key Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `restore.sh` | Full system restore after fresh OpenClaw install | `bash restore.sh` |
| `sync.sh` | Sync workspace files to brain repo and push to GitHub | `bash sync.sh` or `bash sync.sh "custom message"` |

## Rules

- R2D2 commits here after every meaningful session
- Never delete history — amend or add, never force-push
- Human-readable always — Suhail should be able to read any file on GitHub
- Self-improvement: observe → research → test → document → push
