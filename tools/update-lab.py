#!/usr/bin/env python3
"""
update-lab.py — Dynamically update the lab site with current project/agent state.

R2D2 and 3PO call this after any meaningful work session.
It updates lab.ts data, rebuilds, and redeploys — no manual intervention needed.

Usage:
  python3 /home/r2d2/tools/update-lab.py

  Or with inline overrides:
  python3 /home/r2d2/tools/update-lab.py --project "The Headlines Today" --status live --desc "Updated description"
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path

LAB_DATA = Path("/home/r2d2/projects/lab-site/src/data/lab.ts")
LAB_DIR  = Path("/home/r2d2/projects/lab-site")

# ─────────────────────────────────────────────
# SINGLE SOURCE OF TRUTH — update this whenever
# a project ships, stalls, or a new one starts.
# ─────────────────────────────────────────────
AGENTS = [
    {"id": "r2d2",    "name": "R2D2",    "emoji": "🤖", "role": "Orchestrator & Chief of Staff",         "status": "online",    "statusLabel": "Always Online",   "description": "The brain of the operation. Coordinates all agents, handles communications across WhatsApp, manages memory, and dispatches work to the team. Built on Claude Sonnet.",                                                                                                        "tags": ["Orchestration", "Memory", "WhatsApp", "Claude"]},
    {"id": "guardian","name": "Guardian","emoji": "🛡️", "role": "Infrastructure Watchdog",               "status": "online",    "statusLabel": "Running 24/7",    "description": "Silent sentinel monitoring all services — OpenClaw, containers, Nginx. Self-heals before anyone notices. Only alerts when human action is needed.",                                                                                                                           "tags": ["Docker", "Self-healing", "Monitoring", "Infra"]},
    {"id": "maxwell", "name": "Maxwell", "emoji": "📰", "role": "Senior News Editor",                     "status": "scheduled", "statusLabel": "Daily at 5AM EST", "description": "Autonomous news editor that curates The Headlines Today every morning. Pulls global news, writes summaries, generates PDF + audio briefing covering all headlines across all sections.",                                                                               "tags": ["News", "PDF", "Audio", "Daily"]},
    {"id": "3po",     "name": "3PO",     "emoji": "🧑‍💻","role": "Senior Coding Partner & Swarm Lead",  "status": "ondemand",  "statusLabel": "On Demand",       "description": "Claude Code instance spawned for any engineering task. Works solo or deploys as a parallel swarm — multiple instances tackling independent workstreams simultaneously. Builds features, fixes bugs, writes architecture.",                                          "tags": ["Claude Code", "Full-Stack", "Swarm", "Architecture"]},
    {"id": "yoda",    "name": "Yoda",    "emoji": "🧙", "role": "Self-Evolving Research Agent",           "status": "learning",  "statusLabel": "Learning",        "description": "Feeds on research papers and builds its own VL-JEPA model. Extracts knowledge, updates understanding, improves code autonomously. Currently at v0.5 — 161M parameters.",                                                                                                "tags": ["VL-JEPA", "Self-Evolving", "PyTorch", "Research"]},
    {"id": "aria",    "name": "ARIA",    "emoji": "🎯", "role": "AI HR & Career Intelligence",            "status": "ondemand",  "statusLabel": "On Demand",       "description": "Tailors resumes for ATS + human readers, optimizes LinkedIn, generates portfolio sites, career strategy. Every candidate is a brand. Top 1% globally.",                                                                                                                "tags": ["Career", "Resume", "LinkedIn", "Branding"]},
]

PROJECTS = [
    {
        "name": "The Headlines Today",
        "status": "live",
        "stack": ["React", "TypeScript", "Vite", "Claude AI", "Docker", "Nginx"],
        "description": "AI-curated daily newspaper. Maxwell fetches global RSS feeds, writes publication-ready summaries, generates PDF + audio briefing covering all headlines — published every morning at 5 AM EST.",
        "url": "https://news.suhailtaj.cloud",
    },
    {
        "name": "Prompt Studio",
        "status": "live",
        "stack": ["React", "Node.js", "Docker", "Nginx"],
        "description": "A personal prompt engineering workspace. Design, test, and iterate on prompts for LLMs with a clean, focused interface.",
        "url": "https://lab.suhailtaj.cloud/prompt-studio/",
    },
    {
        "name": "Yoda — VL-JEPA Learning System",
        "status": "active",
        "stack": ["Python", "PyTorch", "Claude", "BERT", "ViT", "Docker"],
        "description": "Self-evolving agent that learns Vision-Language JEPA from research papers and autonomously builds its own product embedding model. v0.5 — 161M parameters, trained on Amazon Berkeley Objects dataset.",
        "url": None,
    },
]

FOCUS_ITEMS = [
    {"emoji": "📰", "text": "The Headlines Today — AI newspaper publishing daily at 5AM EST via Maxwell"},
    {"emoji": "🧪", "text": "Prompt Studio — Live prompt engineering workspace at lab.suhailtaj.cloud"},
    {"emoji": "🧙", "text": "Yoda — Self-evolving VL-JEPA agent, v0.5 with 161M parameters"},
    {"emoji": "🧠", "text": "VL-JEPA — Training a vision-language model from research papers"},
]

STATUS_COLORS = {
    "online":    "#22c55e",
    "scheduled": "#f59e0b",
    "ondemand":  "#3b82f6",
    "learning":  "#a855f7",
}


def render_lab_ts(agents, projects, focus_items, status_colors):
    """Render the lab.ts TypeScript data file.
    
    Stats are computed dynamically from actual data:
    - agents: count of all agents
    - liveProjects: count of projects with status='live'
    - activeProjects: count of projects with status='active'
    - modelTraining: count of projects with 'PyTorch' or 'training' in stack/description
    
    focusItems is always trimmed to exactly 4 (most recent = highest priority).
    """

    def ts_str(s):
        if s is None:
            return "undefined"
        return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"

    def ts_arr(arr):
        return "[" + ", ".join(ts_str(i) for i in arr) + "]"

    # Always exactly 4 focus items — trim to first 4 if more provided
    focus_items_4 = focus_items[:4]

    agent_lines = []
    for a in agents:
        agent_lines.append(
            f"  {{ id: {ts_str(a['id'])}, name: {ts_str(a['name'])}, emoji: {ts_str(a['emoji'])}, "
            f"role: {ts_str(a['role'])}, status: {ts_str(a['status'])} as const, "
            f"statusLabel: {ts_str(a['statusLabel'])}, description: {ts_str(a['description'])}, "
            f"tags: {ts_arr(a['tags'])} }},"
        )

    project_lines = []
    for p in projects:
        url_part = f"url: {ts_str(p['url'])}," if p.get("url") else ""
        project_lines.append(
            f"  {{ name: {ts_str(p['name'])}, status: {ts_str(p['status'])} as const, "
            f"stack: {ts_arr(p['stack'])}, description: {ts_str(p['description'])}, {url_part} }},"
        )

    color_lines = []
    for k, v in status_colors.items():
        color_lines.append(f"  {k}: {ts_str(v)},")

    focus_lines = []
    for fi in focus_items_4:
        focus_lines.append(f"  {{ emoji: {ts_str(fi['emoji'])}, text: {ts_str(fi['text'])} }},")

    # Compute stats dynamically
    agent_count   = len(agents)
    live_count    = sum(1 for p in projects if p["status"] == "live")
    active_count  = sum(1 for p in projects if p["status"] == "active")
    model_count   = sum(1 for p in projects if "PyTorch" in p.get("stack", []) or
                        any(w in p.get("description", "").lower() for w in ["model", "training", "jepa"]))

    from datetime import datetime
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    return f"""// AUTO-GENERATED by update-lab.py — do not edit manually
// Last updated: {updated_at} by R2D2/3PO

export interface Agent {{
  id: string
  name: string
  emoji: string
  role: string
  status: 'online' | 'scheduled' | 'ondemand' | 'learning'
  statusLabel: string
  description: string
  tags: string[]
}}

export interface Project {{
  name: string
  status: 'live' | 'active' | 'planned'
  stack: string[]
  description: string
  url?: string
}}

export interface FocusItem {{
  emoji: string
  text: string
}}

export const agents: Agent[] = [
{chr(10).join(agent_lines)}
]

export const projects: Project[] = [
{chr(10).join(project_lines)}
]

// Always exactly 4 items — highest priority current work
export const focusItems: FocusItem[] = [
{chr(10).join(focus_lines)}
]

// Dynamically computed from actual data above
export const labStats = {{
  agents: {agent_count},
  liveProjects: {live_count},
  activeProjects: {active_count},
  modelTraining: {model_count},
}}

export const statusColors: Record<string, string> = {{
{chr(10).join(color_lines)}
}}
"""


def rebuild_and_deploy():
    print("🔨 Building lab site...")
    r = subprocess.run(["npm", "run", "build"], cwd=LAB_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ Build failed:\n{r.stderr}")
        return False
    print("✅ Build succeeded")

    print("🚀 Deploying...")
    r = subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=LAB_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ Deploy failed:\n{r.stderr}")
        return False
    print("✅ Deployed — lab.suhailtaj.cloud updated")
    return True


def commit_and_push(message="chore: auto-update lab data"):
    subprocess.run(["git", "add", "-A"], cwd=LAB_DIR)
    subprocess.run(["git", "commit", "-m", message], cwd=LAB_DIR)
    subprocess.run(["git", "push", "origin", "development"], cwd=LAB_DIR)
    print("✅ Committed and pushed to development")


def main():
    parser = argparse.ArgumentParser(description="Update the lab site dynamically")
    parser.add_argument("--dry-run", action="store_true", help="Print generated lab.ts without writing")
    parser.add_argument("--message", default="chore: auto-update lab — R2D2 session sync", help="Git commit message")
    args = parser.parse_args()

    print("🧪 Updating lab site data...")

    ts_content = render_lab_ts(AGENTS, PROJECTS, FOCUS_ITEMS, STATUS_COLORS)

    if args.dry_run:
        print(ts_content)
        return

    LAB_DATA.write_text(ts_content)
    print(f"✅ Updated {LAB_DATA}")

    if not rebuild_and_deploy():
        sys.exit(1)

    commit_and_push(args.message)
    print("\n✅ Lab site is live and up to date.")


if __name__ == "__main__":
    main()
