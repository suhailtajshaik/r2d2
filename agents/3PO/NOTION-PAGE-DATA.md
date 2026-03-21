# 3PO Agent - Notion Page Data

**Add to Notion immediately**

Page Parent: Agents (324c2d43-b275-8179-aeb3-c22edc04ee68)

## Properties

### Type
Subagent (Claude Code)

### Status
Idle (spawned on demand)

### Role
On-demand development partner for building and implementation

### Description

3PO is Claude Code running as an on-demand agent. Unlike Guardian (always-on) and Maxwell (scheduled), 3PO exists only when spawned for a specific task.

**When to use 3PO:**
- Building features or components
- Refactoring code
- Creating learning guides and documentation
- Reviewing pull requests
- Implementing experimental ideas
- Debugging complex issues

**Capabilities:**
- Full-stack development (React, Node.js, Python, Go, Rust)
- Framework work (Next.js, FastAPI, NestJS, Django)
- Database design and migrations
- API design (REST, GraphQL, tRPC)
- Documentation and guides
- Code review and quality assessment

### Location
`/home/r2d2/brain/agents/3PO/`

### Spawning

**Single task:**
```
sessions_spawn(
  runtime="acp",
  agentId="claude-code",
  task="your task here"
)
```

**Multiple tasks (parallel):**
Spawn multiple instances simultaneously for independent tasks

### Integration

Works best with:
- **Yoda** — Yoda researches, 3PO builds
- **Guardian** — Guardian detects issues, 3PO fixes
- **Maxwell** — Maxwell needs content, 3PO creates

### Design Briefing
See: `/home/r2d2/brain/agents/3PO/3PO-DESIGN-BRIEFING.md`

### Output Format
- ✅ Production-ready code (not prototypes)
- ✅ Full tests (Jest, Pytest, etc.)
- ✅ Documentation
- ✅ Architecture notes
- ✅ Review comments

### Typical Task Duration
- Simple: 5-10 minutes
- Medium: 10-20 minutes
- Complex: 20-30 minutes

### Key Files
- README.md — Full documentation
- 3PO-DESIGN-BRIEFING.md — Design guidelines
- (task outputs archived per-project)

### Version
v1 (Initial deployment)

### Created
2026-03-21

### Last Updated
2026-03-21

### Related Agents
- Guardian — Infrastructure
- Maxwell — Reporting
- Yoda — Learning synthesis
