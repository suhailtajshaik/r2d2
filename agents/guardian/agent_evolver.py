"""
Agent Evolver — Guardian module.

Every agent evolves over time. This runs weekly per agent:
1. Researches latest techniques for that agent's domain
2. Identifies gaps vs current capability
3. Comes up with creative improvements (new tools, methods, prompts)
4. Dispatches 3PO/Swarm Troopers to implement
5. Logs what changed and why

Goal: agents that are measurably better every week.
Like a human professional who reads, learns, experiments — but 24/7.
"""

import os
import json
import subprocess
import hashlib
from datetime import datetime, timedelta
import logging

AGENTS_DIR = "/home/r2d2/brain/agents"
EVOLUTION_LOG = "/home/r2d2/guardian/agent_evolution.json"
WORKSPACE_SKILLS = "/home/r2d2/.openclaw/workspace/skills"
EVOLUTION_INTERVAL_DAYS = 7
log = logging.getLogger("guardian")


# Agent registry — what each agent does and how to research improvements
AGENT_REGISTRY = {
    "guardian": {
        "domain": "infrastructure monitoring, self-healing systems, AI operations",
        "research_queries": [
            "self-healing infrastructure best practices 2026",
            "AI agent monitoring techniques autonomous systems",
            "predictive failure detection VPS monitoring",
            "chaos engineering techniques for AI systems"
        ],
        "improvement_areas": [
            "Add predictive checks (catch issues before they happen, not after)",
            "Improve issue pattern recognition across knowledge.json",
            "Add network latency monitoring",
            "Smarter 3PO dispatch — include context from knowledge.json in repair prompts"
        ],
        "source": "/home/r2d2/guardian/",
        "spec": "/home/r2d2/brain/agents/guardian/README.md"
    },
    "maxwell": {
        "domain": "journalism, news editing, content quality, editorial standards",
        "research_queries": [
            "AI journalism best practices 2026",
            "Reuters AP style guide updates news writing",
            "news aggregation quality scoring techniques",
            "audience engagement in digital news 2026"
        ],
        "improvement_areas": [
            "Add story importance scoring (not all news is equal)",
            "Source credibility weighting — BBC vs unknown blog",
            "Add trending/viral detection from HN upvotes",
            "Improve Hyderabad and India news sourcing",
            "Add sentiment detection to flag sensitive stories"
        ],
        "source": "/home/r2d2/tools/editor-agent/",
        "spec": "/home/r2d2/brain/agents/maxwell/README.md"
    },
    "aria": {
        "domain": "HR, recruiting, career development, personal branding, resume optimization",
        "research_queries": [
            "ATS resume optimization techniques 2026 AI era",
            "personal branding strategies top candidates 2026",
            "LinkedIn algorithm changes 2026 career visibility",
            "AI recruitment trends hiring manager psychology 2026",
            "skills in demand global job market 2026"
        ],
        "improvement_areas": [
            "Add real-time salary data scraping for benchmarking",
            "Integrate job board scanning (LinkedIn, Indeed) for market signals",
            "Add interview question prediction based on job description",
            "Build candidate progress tracker (application → interview → offer pipeline)",
            "Add industry-specific resume templates (tech, finance, healthcare, etc.)"
        ],
        "source": "/home/r2d2/projects/aria/",
        "spec": "/home/r2d2/brain/agents/aria/ARIA.md"
    },
    "3po": {
        "domain": "software engineering, coding patterns, architecture, debugging",
        "research_queries": [
            "Claude Code best practices autonomous coding 2026",
            "AI coding agent prompt engineering techniques",
            "software architecture patterns 2026 MERN stack",
            "code review automation techniques AI"
        ],
        "improvement_areas": [
            "Improve TODO.md task format for better context",
            "Add pre-flight checks before coding (read existing tests, understand constraints)",
            "Better git commit message patterns",
            "Add post-task verification step (run tests, check build)"
        ],
        "source": "/home/r2d2/brain/agents/3po/",
        "spec": "/home/r2d2/brain/agents/3po/README.md"
    }
}


def load_evolution_log():
    if os.path.exists(EVOLUTION_LOG):
        with open(EVOLUTION_LOG) as f:
            try:
                return json.load(f)
            except:
                pass
    return {"agents": {}, "last_run": None}


def save_evolution_log(log_data):
    with open(EVOLUTION_LOG, "w") as f:
        json.dump(log_data, f, indent=2, default=str)


def should_evolve_agent(agent_name, log_data):
    agent_log = log_data.get("agents", {}).get(agent_name, {})
    last_evolved = agent_log.get("last_evolved")
    if not last_evolved:
        return True
    last_dt = datetime.fromisoformat(last_evolved)
    return (datetime.now() - last_dt).days >= EVOLUTION_INTERVAL_DAYS


def get_next_agent_to_evolve(log_data):
    """Pick the agent that hasn't been evolved longest."""
    candidates = []
    for agent_name in AGENT_REGISTRY:
        agent_log = log_data.get("agents", {}).get(agent_name, {})
        last_evolved = agent_log.get("last_evolved")
        if not last_evolved:
            candidates.append((agent_name, datetime.min))
        else:
            last_dt = datetime.fromisoformat(last_evolved)
            if (datetime.now() - last_dt).days >= EVOLUTION_INTERVAL_DAYS:
                candidates.append((agent_name, last_dt))

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[1])
    return candidates[0][0]


def evolve_agent(agent_name):
    """Research + improve an agent. Dispatch 3PO to implement."""
    config = AGENT_REGISTRY.get(agent_name)
    if not config:
        return "Unknown agent"

    # Read current spec
    spec_path = config.get("spec", "")
    current_spec = ""
    if os.path.exists(spec_path):
        with open(spec_path) as f:
            current_spec = f.read()[:3000]

    # Build research queries
    queries = config.get("research_queries", [])
    research_results = []
    for query in queries[:3]:  # Top 3 queries
        try:
            result = subprocess.run(
                ["python3", "/home/r2d2/tools/websearch.py", "--summary", query],
                capture_output=True, text=True, timeout=30
            )
            if result.stdout.strip():
                research_results.append(f"Query: {query}\n{result.stdout[:500]}")
        except:
            pass

    research_text = "\n\n".join(research_results) if research_results else "No research results"
    improvement_areas = "\n".join(f"- {a}" for a in config.get("improvement_areas", []))

    prompt = f"""You are the Agent Evolution System. Your job: make the {agent_name.upper()} agent measurably better.

AGENT: {agent_name}
DOMAIN: {config['domain']}
SOURCE: {config['source']}
SPEC: {spec_path}

CURRENT SPEC (summary):
---
{current_spec[:2000]}
---

MARKET RESEARCH (latest findings):
---
{research_text[:2000]}
---

KNOWN IMPROVEMENT AREAS:
{improvement_areas}

YOUR TASK — be creative, think like a human expert who just read the latest research:

1. **Identify 2-3 concrete improvements** that would make {agent_name} meaningfully better today
   - Not theoretical — actual code/prompt/config changes
   - Prioritize: impact on quality > complexity of implementation
   - Consider what's NEW in 2026 that this agent isn't using yet

2. **Implement the top improvement** right now:
   - Make the actual change (edit files in {config['source']})
   - Update the spec at {spec_path}
   - If it's a prompt improvement, update the relevant .md file
   - If it's a new capability, add it to the agent's code

3. **Test it works** (run the agent briefly if possible)

4. **Document the change:**
   - What changed and why
   - Expected impact
   - How to measure improvement
   - Write to: /home/r2d2/brain/agents/{agent_name}/CHANGELOG.md (append)

5. **Sync to brain:**
   - cp -r {config['source']} /home/r2d2/brain/agents/{agent_name}/
   - git -C /home/r2d2/brain add -A
   - git -C /home/r2d2/brain commit -m "evolve({agent_name}): [what improved] — $(date +%Y-%m-%d)"
   - git -C /home/r2d2/brain push origin master

6. **Log result** — print: EVOLUTION_RESULT: [one sentence on what was improved and expected impact]

Be creative. Think beyond the obvious. What would a top expert in {config['domain']} suggest?
What techniques are the best teams using that this agent isn't?
"""

    log.info(f"AGENT EVOLUTION: evolving {agent_name}...")

    result = subprocess.run(
        ["claude", "--permission-mode", "bypassPermissions", "--print", prompt],
        capture_output=True, text=True, timeout=600
    )

    # Extract result note
    note = f"Evolved {agent_name} — see CHANGELOG"
    for line in result.stdout.split("\n"):
        if line.startswith("EVOLUTION_RESULT:"):
            note = line.replace("EVOLUTION_RESULT:", "").strip()
            break

    return note


def run_agent_evolution():
    """Entry point called by Guardian. Evolves one agent per day."""
    log_data = load_evolution_log()
    now = datetime.now()

    # Only run once per day
    last_run = log_data.get("last_agent_evolution_run")
    if last_run:
        last_dt = datetime.fromisoformat(last_run)
        if (now - last_dt).total_seconds() < 86400:
            return

    agent = get_next_agent_to_evolve(log_data)
    if not agent:
        log_data["last_agent_evolution_run"] = now.isoformat()
        save_evolution_log(log_data)
        return

    note = evolve_agent(agent)

    # Update log
    log_data.setdefault("agents", {})[agent] = {
        "last_evolved": now.isoformat(),
        "last_improvement": note
    }
    log_data["last_agent_evolution_run"] = now.isoformat()
    save_evolution_log(log_data)

    log.info(f"AGENT EVOLUTION DONE: {agent} — {note}")


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    agent = sys.argv[1] if len(sys.argv) > 1 else get_next_agent_to_evolve(load_evolution_log())
    if agent:
        print(f"Evolving: {agent}")
        note = evolve_agent(agent)
        print(f"Result: {note}")
    else:
        print("All agents current")
