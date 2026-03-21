# 3PO - Claude Code Coding Partner

**On-demand development agent for building and implementation**

## Overview

3PO is Claude Code running in the background, spawned on-demand for coding tasks. Unlike Guardian (always running) and Maxwell (scheduled), 3PO is ephemeral — it exists for a specific task, then terminates.

## Purpose

When you need to:
- Build a feature
- Refactor code
- Review pull requests
- Create learning guides
- Debug complex issues
- Implement experimental ideas

You spawn 3PO, give it a task, and it runs to completion. Result comes back as implemented code, documentation, or generated content.

## How It Works

### Spawn 3PO
```bash
claude --permission-mode bypassPermissions --print 'your task here'
```

### Task Examples
- "Build a React component for [feature]"
- "Refactor this Python code for performance"
- "Create a system design guide on [topic]"
- "Implement GraphQL API with these mutations"
- "Write comprehensive tests for [module]"

### Output
- ✅ Implemented code (ready to use)
- ✅ Documentation (README, guides, API docs)
- ✅ Tests (Jest, Pytest, etc.)
- ✅ Architecture notes
- ✅ Review comments

## Status

**Mode:** Ephemeral (spawned on demand)
**Runtime:** Claude Code CLI
**Session Type:** One-shot or persistent thread-bound

## Integration

3PO works best with:
- **Yoda** — For research + learning guide synthesis
  - Yoda researches topic → 3PO implements → delivers to user
  - Example: "Research AI agents" → "Build example code"

- **Guardian** — For infrastructure code
  - Guardian detects issue → 3PO fixes → implements solution
  - Example: "Container crashes" → "Diagnose + patch"

- **Maxwell** — For content generation
  - Maxwell identifies need → 3PO creates guide/script
  - Example: "Market report needed" → "Create 20-page analysis"

## Capabilities

### Code
- Full-stack development (React, Node.js, Python, Go, Rust)
- Framework-specific work (Next.js, FastAPI, NestJS, Django)
- Database design (SQL, NoSQL, migrations)
- API design (REST, GraphQL, tRPC)

### Documentation
- Comprehensive guides (with examples, diagrams, checklists)
- API documentation (OpenAPI, GraphQL SDL)
- Architecture documentation (C4 diagrams, decision records)
- Learning materials (tutorials, cheat sheets)

### Analysis
- Code review and quality assessment
- Performance analysis and optimization
- Security audit and fixes
- Complexity analysis

### Content
- Technical articles and blog posts
- Tutorial content and how-tos
- Product documentation
- Training materials

## Performance

- **Speed:** 5-30 minutes per task (depending on complexity)
- **Quality:** Production-ready code, not prototypes
- **Cost:** Minimal (runs locally via Claude Code)
- **Output:** Complete, tested, documented

## Working with 3PO

### Best Practices
1. **Be specific** — Clear task = better results
2. **Provide context** — What's the goal? What's the context?
3. **Set constraints** — Tech stack? Performance requirements? Limitations?
4. **Ask for output format** — Code only? With tests? Documented?

### Example Task
```
Build a React component for a modal dialog with:
- Dark mode support (use Tailwind)
- Accessibility (ARIA labels, keyboard navigation)
- Animation on open/close (Framer Motion)
- TypeScript strict mode
- Jest + React Testing Library tests

Output: Component file + stories file + test file + usage example
```

## Limitations

- ❌ Can't commit code directly (R2D2 does)
- ❌ Can't deploy directly (Guardian handles CI/CD)
- ❌ Can't update Notion (that's R2D2)
- ❌ Can't run long-running services (that's Guardian/Maxwell)

**Why:** Separation of concerns. 3PO builds, others deploy.

## Integration with Brain

**Location:** `/home/r2d2/brain/agents/3PO/`

This is where:
- Task templates live
- Design briefings are stored
- Output from 3PO runs are archived
- Integration patterns are documented

See: `/home/r2d2/brain/agents/3PO/3PO-DESIGN-BRIEFING.md`

## Spawning Patterns

### Single Task
```bash
sessions_spawn(
  runtime="acp",
  agentId="claude-code",
  task="Build feature X"
)
# Returns immediately
# 3PO runs in background
# Result pushed to you when done
```

### Multiple Parallel Tasks
```bash
# Spawn 3 instances (R3PO Swarm Troopers)
sessions_spawn(...task1...)  # Returns immediately
sessions_spawn(...task2...)  # Returns immediately
sessions_spawn(...task3...)  # Returns immediately
# All 3 run in parallel
# Results come back as they finish
```

### Team Workflow
```
Yoda researches → delivers brief
3PO reads brief → builds code
Guardian tests → deploys
R2D2 updates docs → syncs Notion
```

## Future Enhancements

- [ ] Code review agent (paired with 3PO)
- [ ] Performance testing agent
- [ ] Security audit agent
- [ ] Documentation generation agent
- [ ] Automated refactoring suggestions

---

**Created:** 2026-03-21
**Last Updated:** 2026-03-21
**Status:** Active and operational
