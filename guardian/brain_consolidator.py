"""
Brain Consolidator — Guardian module for daily brain consolidation.

Like human sleep memory consolidation:
  Raw daily logs (hippocampus) → distilled long-term memory (cortex)

Goals:
- Extract high-signal insights from daily logs
- Compress MEMORY.md — keep it lean, dense, useful
- Remove stale/redundant/outdated info
- Identify patterns across sessions
- Build a sharper, smaller, smarter brain over time

Runs daily. Uses 3PO (Claude) to do the actual consolidation.
"""

import os
import subprocess
import json
import glob
from datetime import datetime, timedelta

MEMORY_FILE = "/home/r2d2/brain/workspace/MEMORY.md"
BRAIN_MEMORY = "/home/r2d2/brain/workspace/MEMORY.md"
DAILY_LOGS_DIR = "/home/r2d2/brain/memory"
BRAIN_DAILY_DIR = "/home/r2d2/brain/memory"
CONSOLIDATION_LOG = "/home/r2d2/guardian/consolidation_log.json"
CONSOLIDATION_INTERVAL_HOURS = 24


def load_consolidation_log():
    if os.path.exists(CONSOLIDATION_LOG):
        with open(CONSOLIDATION_LOG) as f:
            try:
                return json.load(f)
            except:
                pass
    return {"last_run": None, "consolidations": 0}


def save_consolidation_log(log):
    with open(CONSOLIDATION_LOG, "w") as f:
        json.dump(log, f, indent=2, default=str)


def should_consolidate():
    log = load_consolidation_log()
    if not log.get("last_run"):
        return True
    last = datetime.fromisoformat(log["last_run"])
    return (datetime.now() - last).total_seconds() >= CONSOLIDATION_INTERVAL_HOURS * 3600


def read_recent_daily_logs(days=3):
    """Read the last N days of daily memory logs."""
    logs = {}
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        for log_dir in [DAILY_LOGS_DIR, BRAIN_DAILY_DIR]:
            path = os.path.join(log_dir, f"{date}.md")
            if os.path.exists(path):
                with open(path) as f:
                    logs[date] = f.read()
                break
    return logs


def read_current_memory():
    for path in [MEMORY_FILE, BRAIN_MEMORY]:
        if os.path.exists(path):
            with open(path) as f:
                return f.read()
    return ""


def run_consolidation():
    """
    Dispatch 3PO to consolidate the brain.
    Like REM sleep — compress, distill, strengthen important memories.
    """
    import logging
    log = logging.getLogger("guardian")

    daily_logs = read_recent_daily_logs(days=3)
    current_memory = read_current_memory()

    daily_content = ""
    for date, content in sorted(daily_logs.items(), reverse=True):
        daily_content += f"\n\n=== {date} ===\n{content[:2000]}"

    prompt = f"""You are R2D2's brain consolidator. Your job is like human sleep memory consolidation — take raw daily experience logs and distill them into a sharper, leaner long-term memory.

GOAL: Make the brain as complex as a human brain with AI superpowers, but with LESS memory. Dense, high-signal, no waste.

CURRENT MEMORY.md (long-term memory):
---
{current_memory[:4000]}
---

RECENT DAILY LOGS (raw experiences, last 3 days):
---
{daily_content[:4000]}
---

YOUR TASK — consolidate following these principles:

1. **Extract new learnings** from daily logs that aren't in MEMORY.md yet
   - New facts about Suhail, his projects, preferences, decisions
   - New rules or patterns that emerged
   - Technical knowledge worth keeping

2. **Compress redundant info** — if something is stated 3 ways, keep the best 1
   - Merge similar entries
   - Remove outdated info (e.g. old VPS IPs, completed tasks)
   - Shorten verbose sections without losing meaning

3. **Strengthen important patterns** — things that came up multiple times = important
   - Reinforce rules that keep getting violated or forgotten
   - Surface patterns in how Suhail works and thinks

4. **Never delete critical info:**
   - Suhail's identity, contacts, preferences
   - Active project status
   - Operating rules (git workflow, docker, naming, etc.)
   - Agent roster and their roles

5. **Format for density** — every line must earn its place
   - No full sentences where a phrase works
   - No repetition
   - Structured, scannable

Output ONLY the new complete MEMORY.md content. Nothing else. No preamble. Start with # MEMORY.md
The output should be SHORTER or equal in length to the current MEMORY.md, never longer, unless genuinely new critical info was added.
"""

    log.info("BRAIN CONSOLIDATION: starting daily consolidation...")

    result = subprocess.run(
        ["claude", "--permission-mode", "bypassPermissions", "--print", prompt],
        capture_output=True, text=True, timeout=300
    )

    output = result.stdout.strip()

    if not output or "# MEMORY.md" not in output and "## " not in output:
        log.warning("BRAIN CONSOLIDATION: 3PO returned empty or invalid output — skipping")
        return False

    # Extract just the MEMORY.md content
    if "# MEMORY.md" in output:
        output = output[output.index("# MEMORY.md"):]

    # Write consolidated memory
    with open(MEMORY_FILE, "w") as f:
        f.write(output)

    # Sync to brain
    with open(BRAIN_MEMORY, "w") as f:
        f.write(output)

    # Commit to git
    subprocess.run([
        "git", "-C", "/home/r2d2/brain", "add", "-A"
    ], capture_output=True)
    subprocess.run([
        "git", "-C", "/home/r2d2/brain", "commit",
        "-m", f"brain: daily consolidation — {datetime.now().strftime('%Y-%m-%d')}"
    ], capture_output=True)
    subprocess.run([
        "git", "-C", "/home/r2d2/brain", "push", "origin", "master"
    ], capture_output=True)

    # Update consolidation log
    clog = load_consolidation_log()
    clog["last_run"] = datetime.now().isoformat()
    clog["consolidations"] = clog.get("consolidations", 0) + 1
    save_consolidation_log(clog)

    log.info(f"BRAIN CONSOLIDATION: done — consolidation #{clog['consolidations']}")
    return True


def run_brain_consolidation():
    """Entry point called by Guardian."""
    if should_consolidate():
        run_consolidation()


if __name__ == "__main__":
    print("Running brain consolidation...")
    success = run_consolidation()
    print("Done ✓" if success else "Skipped or failed")
