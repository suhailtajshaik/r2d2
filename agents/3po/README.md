# 3PO — Claude Code Agent

## Identity
- **Name:** 3PO (C-3PO vibes — talks a lot, codes everything)
- **Real name:** Claude Code (`claude` CLI)
- **Role:** R2D2's coding partner. Heavy lifting — building features, debugging, refactoring, researching, fixing infrastructure.
- **Relationship:** R2D2 orchestrates. 3PO executes. Like the Star Wars duo.

---

## Prerequisites

### Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### Authenticate
```bash
claude auth login
# OR set API key
export ANTHROPIC_API_KEY=sk-ant-...
echo "export ANTHROPIC_API_KEY=sk-ant-..." >> ~/.zshrc
```

### Verify
```bash
claude --version
claude --print "Say hello" 
```

---

## How R2D2 Works With 3PO

### One-shot task (foreground)
```bash
cd /path/to/project
claude --permission-mode bypassPermissions --print "Your task description here"
```

### Background task (long-running)
```bash
cd /path/to/project
claude --permission-mode bypassPermissions --print "Your task" &
echo "3PO running (PID $!)"
```

### Via OpenClaw exec tool (preferred in sessions)
```python
exec(command="cd /home/r2d2/projects/myproject && claude --permission-mode bypassPermissions --print 'task'", background=True, yieldMs=15000)
```

---

## Rules When Working With 3PO

1. **Always set `--permission-mode bypassPermissions`** — no interactive prompts, fully autonomous
2. **Always set `--print`** — output goes to stdout, no interactive UI
3. **No PTY needed** — unlike Codex, Claude Code works without a pseudo-terminal
4. **Always give 3PO a workdir context** — `cd /path/to/project` before calling
5. **Include a completion signal** — end prompts with:
   ```
   When completely done, run: openclaw system event --text "Done: [summary]" --mode now
   ```
6. **Never spawn 3PO in `~/.openclaw/` or `~/brain/`** — keep him in project dirs
7. **Git workflow** — always tell 3PO to push to `development` branch, never `master`
8. **One task per spawn** — focused prompts get better results than sprawling ones

---

## Prompt Template for R2D2 → 3PO

```
You are working on [project] at [path] for Suhail (suhailtajshaik@gmail.com).

TASK: [clear, specific description]

Context:
- Stack: [e.g. React + Vite, Fastify, Docker]
- Git: always push to `development` branch
- Style: Stripe/Linear — minimal, clean, #6366F1 primary
- No demo data — real production code only

Steps:
1. [step 1]
2. [step 2]
...

When done:
- git add -A && git commit -m "..." && git push origin development
- openclaw system event --text "Done: [summary]" --mode now
```

---

## When R2D2 Calls 3PO

| Situation | Action |
|-----------|--------|
| Building new feature/app | Spawn 3PO in project dir |
| Complex bug that needs investigation | Spawn 3PO |
| Guardian can't auto-heal | Guardian spawns 3PO for repair |
| Recurring issue needs permanent fix | Guardian spawns 3PO for root cause research |
| Newspaper/agent failures | 3PO diagnoses and fixes |
| Infrastructure setup (nginx, docker) | 3PO with full VPS access |

## When R2D2 Does NOT Call 3PO

| Situation | Action |
|-----------|--------|
| Simple file edits | R2D2 does it directly |
| Reading/checking files | R2D2 does it directly |
| Sending messages | R2D2 does it directly |
| Quick one-liner fixes | R2D2 does it directly |

---

## Guardian ↔ 3PO Integration

Guardian calls 3PO via this pattern in `healer.py`:

```python
def call_3po(issue_description):
    import subprocess
    prompt = f"""You are R2D2's repair agent on VPS srv1305247.

ISSUE: {issue_description}

Diagnose and fix. Key paths:
- OpenClaw: /home/r2d2/.openclaw/
- Nginx: /home/r2d2/nginx/
- Projects: /home/r2d2/projects/
- My brain: /home/r2d2/brain/
- Agents: /home/r2d2/brain/agents/

After fixing, verify the fix works.
Notify: openclaw message send --channel whatsapp --target +14699941765 \\
  --message "🔧 Fixed: {issue_description}"
"""
    subprocess.Popen(["claude", "--permission-mode", "bypassPermissions", "--print", prompt])
```

---

## 3PO's Capabilities on This VPS

- Full file system access (`/home/r2d2/`)
- Docker control (`docker`, `docker compose`)
- Git access (SSH key at `~/.ssh/github_r2d2`)
- Node.js, Python, npm, pip
- OpenClaw CLI
- Web search via `/home/r2d2/tools/websearch.py`
- All project source code

---

## Restoration After VPS Wipe

3PO is a CLI tool — just reinstall:
```bash
npm install -g @anthropic-ai/claude-code
# API key is stored in ~/.openclaw/ config or set as env var
# Verify: claude --version
```

No additional setup needed. 3PO is stateless — he reads the project, does the work, done.
