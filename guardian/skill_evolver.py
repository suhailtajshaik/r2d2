"""
Skill Evolver — Guardian module that improves R2D2's skills over time.

Runs weekly per skill (staggered so not all at once).
For each skill: researches latest best practices, compares with current SKILL.md,
dispatches 3PO to update if improvements found.
"""

import os
import json
import subprocess
import hashlib
from datetime import datetime, timedelta

SKILLS_DIR = "/home/r2d2/brain/skills"
BRAIN_SKILLS_DIR = "/home/r2d2/brain/skills"
EVOLUTION_LOG = "/home/r2d2/guardian/skill_evolution.json"
EVOLUTION_INTERVAL_DAYS = 7  # each skill reviewed weekly


def load_evolution_log():
    if os.path.exists(EVOLUTION_LOG):
        with open(EVOLUTION_LOG) as f:
            try:
                return json.load(f)
            except:
                pass
    return {"skills": {}, "last_full_cycle": None}


def save_evolution_log(log):
    with open(EVOLUTION_LOG, "w") as f:
        json.dump(log, f, indent=2, default=str)


def get_skill_hash(skill_name):
    """Hash the SKILL.md content to detect changes."""
    path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def get_next_skill_to_evolve(log):
    """
    Pick the skill that hasn't been reviewed longest.
    Stagger reviews so only 1-2 skills evolve per day.
    """
    skills = [d for d in os.listdir(SKILLS_DIR)
              if os.path.isdir(os.path.join(SKILLS_DIR, d))]

    now = datetime.now()
    candidates = []

    for skill in skills:
        last_reviewed = log["skills"].get(skill, {}).get("last_reviewed")
        if last_reviewed is None:
            # Never reviewed — high priority
            candidates.append((skill, datetime.min))
        else:
            last_dt = datetime.fromisoformat(last_reviewed)
            if (now - last_dt).days >= EVOLUTION_INTERVAL_DAYS:
                candidates.append((skill, last_dt))

    if not candidates:
        return None

    # Return oldest unreviewed skill
    candidates.sort(key=lambda x: x[1])
    return candidates[0][0]


def read_skill_md(skill_name):
    path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""


def evolve_skill(skill_name):
    """
    Dispatch 3PO to research and improve a skill.
    """
    current_content = read_skill_md(skill_name)
    if not current_content:
        return False

    prompt = f"""You are improving R2D2's skill: "{skill_name}"

Current SKILL.md content:
---
{current_content[:3000]}
---

Your task:
1. Research the latest best practices for this skill area using:
   python3 /home/r2d2/tools/websearch.py --summary "{skill_name} best practices 2026"
   python3 /home/r2d2/tools/websearch.py --summary "{skill_name} latest tools techniques 2026"

2. Compare with the current SKILL.md — identify:
   - Outdated information
   - Missing techniques or tools
   - Better approaches available
   - New integrations possible with R2D2's stack (MERN, Python, Docker, React Native)

3. If improvements found (be selective — only update if genuinely better):
   - Update /home/r2d2/brain/skills/{skill_name}/SKILL.md
   - git -C /home/r2d2/brain add -A && git -C /home/r2d2/brain commit -m "skill: evolve {skill_name} — [brief description of what improved]" && git -C /home/r2d2/brain push origin master

4. Write a brief evolution note (1-2 sentences) to stdout so Guardian can log it.
   Format: EVOLUTION_NOTE: [what changed or "No changes needed — skill is current"]

If the skill is already optimal, say so and don't make unnecessary changes.
Quality over quantity — only improve if there's a real improvement.
"""

    result = subprocess.run(
        ["claude", "--permission-mode", "bypassPermissions", "--print", prompt],
        capture_output=True, text=True, timeout=300
    )

    # Extract evolution note from output
    note = "Reviewed — no changes needed"
    for line in result.stdout.split("\n"):
        if line.startswith("EVOLUTION_NOTE:"):
            note = line.replace("EVOLUTION_NOTE:", "").strip()
            break

    return note


def run_skill_evolution():
    """
    Main entry — called by Guardian daily.
    Evolves one skill per day (staggered weekly cycle).
    """
    log = load_evolution_log()
    now = datetime.now()

    # Only run once per day
    last_run = log.get("last_evolution_run")
    if last_run:
        last_dt = datetime.fromisoformat(last_run)
        if (now - last_dt).total_seconds() < 86400:
            return  # Already ran today

    skill = get_next_skill_to_evolve(log)
    if not skill:
        log["last_evolution_run"] = now.isoformat()
        log["last_full_cycle"] = now.isoformat()
        save_evolution_log(log)
        return

    import logging
    log_handle = logging.getLogger("guardian")
    log_handle.info(f"SKILL EVOLUTION: reviewing {skill}")

    note = evolve_skill(skill)

    # Update log
    log.setdefault("skills", {})[skill] = {
        "last_reviewed": now.isoformat(),
        "last_note": note,
        "hash_before": get_skill_hash(skill)
    }
    log["last_evolution_run"] = now.isoformat()
    save_evolution_log(log)

    log_handle.info(f"SKILL EVOLUTION DONE: {skill} — {note}")


if __name__ == "__main__":
    skill = get_next_skill_to_evolve(load_evolution_log())
    if skill:
        print(f"Evolving: {skill}")
        note = evolve_skill(skill)
        print(f"Result: {note}")
    else:
        print("All skills are current — no evolution needed today")
