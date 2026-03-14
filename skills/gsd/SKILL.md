# GSD (Get Stuff Done) — R2D2's Task Execution Framework

A structured workflow for breaking down complex work into phases, planning with research, executing with parallel sub-agents, and verifying results.

## Philosophy

- **Spec before code** — Every phase gets a plan before execution
- **Parallel where possible** — Independent tasks run as sub-agents simultaneously  
- **Verify everything** — Each phase gets checked before moving on
- **Fresh context per task** — Sub-agents get clean context windows with only what they need
- **Small atomic tasks** — 2-3 tasks per plan max, each completable in one session

---

## Project Lifecycle

```
┌─────────────────────────────────────┐
│          NEW PROJECT                │
│  gsd:init                           │
│  Discover → Research → Plan Roadmap │
└──────────────┬──────────────────────┘
               │
    ┌──────────▼──────────┐
    │   FOR EACH PHASE:   │
    │                     │
    │  gsd:discuss N      │ ← Lock in preferences with user
    │        ↓            │
    │  gsd:plan N         │ ← Research + plan + verify plan
    │        ↓            │
    │  gsd:execute N      │ ← Parallel sub-agents
    │        ↓            │
    │  gsd:verify N       │ ← Check work against goals
    │        ↓            │
    │  Next phase? ───────┘
    │        │ No
    └────────┼────────────┘
             │
    ┌────────▼────────────┐
    │  gsd:audit           │ ← Final milestone check
    │  gsd:complete        │ ← Archive & tag
    └─────────────────────┘
```

---

## File Structure

All project planning lives in `.gsd/` within the project repo:

```
.gsd/
├── PROJECT.md              # Vision, goals, constraints
├── REQUIREMENTS.md         # Scoped requirements with IDs  
├── ROADMAP.md              # Phase breakdown with status
├── STATE.md                # Current state, blockers, decisions
├── config.json             # Project settings
├── research/               # Domain research outputs
│   └── phase-{N}-research.md
└── phases/
    └── {NN}-{phase-name}/
        ├── CONTEXT.md      # User preferences for this phase
        ├── RESEARCH.md     # Phase-specific research
        ├── PLAN.md         # Execution plan (tasks + dependencies)
        ├── TASKS/
        │   ├── 01-task-name.md   # Individual task specs
        │   └── 02-task-name.md
        ├── EXECUTION.md    # Execution log (what happened)
        └── VERIFICATION.md # Post-execution check results
```

---

## Commands

### Core Workflow

| Command | What It Does |
|---------|-------------|
| `gsd:init` | Initialize project: ask questions, research domain, create requirements + roadmap |
| `gsd:discuss {N}` | Talk through phase N with user to capture preferences/decisions |
| `gsd:plan {N}` | Research + create execution plan for phase N |
| `gsd:execute {N}` | Run phase N tasks via parallel sub-agents |
| `gsd:verify {N}` | Check phase N output against goals |
| `gsd:audit` | Full milestone audit — check all requirements met |
| `gsd:complete` | Archive milestone, git tag, update state |

### Navigation

| Command | What It Does |
|---------|-------------|
| `gsd:status` | Where are we? What's next? |
| `gsd:resume` | Restore context from last session |
| `gsd:quick {desc}` | Ad-hoc task with planning guarantees |

### Phase Management

| Command | What It Does |
|---------|-------------|
| `gsd:add-phase {desc}` | Append new phase to roadmap |
| `gsd:insert-phase {N} {desc}` | Insert urgent phase at position N |
| `gsd:remove-phase {N}` | Remove phase and renumber |

---

## How Each Step Works

### gsd:init — Project Initialization

1. **Discover**: Ask user 5-8 targeted questions about goals, constraints, users, tech stack
2. **Research**: Spawn 3-4 parallel sub-agents to investigate:
   - Stack/technology best practices
   - Competitor/similar solutions
   - Architecture patterns
   - Common pitfalls
3. **Synthesize**: Combine research into PROJECT.md and REQUIREMENTS.md
4. **Roadmap**: Break requirements into 3-8 phases, each with clear deliverables
5. **Present**: Show roadmap to user for approval/refinement

### gsd:plan {N} — Phase Planning

1. **Research**: Spawn sub-agent to deep-dive the phase's domain
2. **Plan**: Create PLAN.md with:
   - Phase goals (from ROADMAP.md)
   - Tasks (2-3 max, each atomic and independent where possible)
   - Dependencies between tasks (determines wave ordering)
   - For each task: files to create/modify, acceptance criteria, verify command
3. **Check**: Review plan against requirements — are we solving the right problem?
4. **Present**: Show plan to user, incorporate feedback

### gsd:execute {N} — Parallel Execution

1. **Analyze dependencies** → group tasks into waves
2. **Wave 1**: Spawn independent tasks as parallel sub-agents
   - Each sub-agent gets: task spec, relevant project context, file paths
   - Each sub-agent commits on completion
3. **Wave 2**: Tasks depending on Wave 1 (spawn after Wave 1 completes)
4. **Log**: Record what each sub-agent did in EXECUTION.md

### gsd:verify {N} — Verification

1. **Automated**: Run test/build/lint commands from plan
2. **Manual check**: Review key files against acceptance criteria
3. **Report**: Create VERIFICATION.md with pass/fail per task
4. **Fix**: If issues found, spawn targeted fix sub-agents

---

## Sub-Agent Task Spec Format

Each task file (`.gsd/phases/NN-name/TASKS/01-task.md`) follows this structure:

```markdown
# Task: {name}

## Goal
One sentence describing what this task accomplishes.

## Context
- Project: {brief description}
- Phase: {phase name and goal}
- Dependencies: {what must exist before this task}

## Scope
### Files to Create/Modify
- `src/components/Foo.tsx` — New component for X
- `src/lib/api.ts` — Add function Y

### Out of Scope
- Don't touch Z
- Don't refactor W

## Acceptance Criteria
- [ ] Component renders correctly
- [ ] API function handles errors
- [ ] Types are correct

## Verify Command
```bash
npm run build && npm run typecheck
```

## Technical Notes
- Use pattern X from existing code
- Follow convention Y
```

---

## Configuration

`.gsd/config.json`:

```json
{
  "mode": "interactive",
  "depth": "standard",
  "parallel_agents": true,
  "verify_after_execute": true,
  "git": {
    "branch_per_phase": false,
    "auto_commit": true
  }
}
```

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| `mode` | `interactive` / `yolo` | `interactive` | `yolo` = auto-approve all steps |
| `depth` | `quick` / `standard` / `comprehensive` | `standard` | 3-5 / 5-8 / 8-12 phases |
| `parallel_agents` | `true` / `false` | `true` | Use sub-agents for execution |
| `verify_after_execute` | `true` / `false` | `true` | Auto-verify after execution |

---

## State Tracking

`.gsd/STATE.md` tracks:

```markdown
# Project State

## Current
- **Milestone**: v1.0
- **Phase**: 3 of 6 (API Layer)
- **Status**: executing
- **Last Updated**: 2026-02-21

## Decisions
- Using Supabase over custom Postgres (Phase 1 discussion)
- REST over GraphQL for simplicity (Phase 2 discussion)

## Blockers
- None

## Completed Phases
- [x] Phase 1: Project Setup (verified ✅)
- [x] Phase 2: Database Schema (verified ✅)
- [ ] Phase 3: API Layer (in progress)
```

---

## Tips

- **Clear context between phases** — each phase should start fresh
- **2-3 tasks per phase max** — smaller is better for sub-agent reliability
- **Always verify** — never skip gsd:verify, it catches 80% of issues
- **Research saves time** — the 2 minutes spent researching prevents 20 minutes of wrong implementation
- **User discussion matters** — gsd:discuss catches preference mismatches before they become rework
