# Prompt Studio Redesign Plan

## Current State
- Basic React + Node.js app at lab.suhailtaj.cloud/prompt-studio/
- Functional but visually plain

## Target: Production-Grade AI Tool UI

Design inspiration: Vercel AI playground, Claude.ai, OpenAI playground.
Design tokens: same as lab/portfolio (dark `#0c1222`, gold `#c9a962`).

## Planned Layout

```
┌─────────────────────────────────────────────────────┐
│  NAV: Prompt Studio  |  Templates  |  History  [☀️] │
├──────────────┬──────────────────────────────────────┤
│              │  PROMPT INPUT PANEL                  │
│  SIDEBAR     │  ┌────────────────────────────────┐  │
│              │  │ System prompt (collapsible)    │  │
│  Templates   │  └────────────────────────────────┘  │
│  Saved       │  ┌────────────────────────────────┐  │
│  History     │  │ User prompt textarea           │  │
│              │  │                                │  │
│              │  └──────────────── [Run ▶] [Copy] ┘  │
│              ├──────────────────────────────────────┤
│              │  OUTPUT PANEL                        │
│              │  Streaming typewriter text           │
│              │  [Copy] [Save] [Rate]                │
└──────────────┴──────────────────────────────────────┘
```

## Components to Use from 21st.dev

1. **Split panel layout** — resizable left/right panels
2. **AI chat bubble style** — for output display
3. **Streaming/typewriter text** — animate output as it arrives
4. **Bento grid** — for template library cards
5. **Glassmorphism sidebar** — template/history nav
6. **Animated Run button** — with loading spinner state
7. **Code block** — for prompt with syntax highlighting
8. **Toast notifications** — copy success, save success

## Model Selector
- Dropdown: Claude Sonnet, Claude Haiku, GPT-4o, GPT-4o mini
- Temperature slider
- Max tokens input

## Tech Stack (keep or upgrade)
- Current: React + Node.js + Docker
- Upgrade option: Next.js App Router (better streaming support)
- Styling: Keep pure CSS with our tokens OR add Tailwind

## Phase 1 (MVP redesign)
- New layout with split panels
- Streaming output with typewriter effect
- Template library (bento grid)
- Dark/light theme (already have tokens)

## Phase 2
- Save/load prompt history (MongoDB — already running)
- Share prompts via URL
- Rate/tag outputs
- Export to markdown/JSON
