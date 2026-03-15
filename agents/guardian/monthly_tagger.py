"""
Monthly Tagger — Guardian module.
Creates a git tag on my brain repo on the 1st of every month.
Brain snapshot: brain-YYYY-MM
"""

import subprocess
import json
import os
from datetime import datetime

MONTHLY_TAG_LOG = "/home/r2d2/guardian/monthly_tag_log.json"


def load_log():
    if os.path.exists(MONTHLY_TAG_LOG):
        with open(MONTHLY_TAG_LOG) as f:
            try:
                return json.load(f)
            except:
                pass
    return {"last_tag": None}


def save_log(log):
    with open(MONTHLY_TAG_LOG, "w") as f:
        json.dump(log, f, indent=2, default=str)


def run_monthly_tag():
    """Create a monthly brain tag on the 1st of each month."""
    now = datetime.now()

    # Only run on the 1st of the month
    if now.day != 1:
        return

    log = load_log()
    month_str = now.strftime("%Y-%m")

    # Don't re-tag the same month
    if log.get("last_tag") == month_str:
        return

    import logging
    logger = logging.getLogger("guardian")
    logger.info(f"MONTHLY TAG: creating brain-{month_str}")

    brain_dir = "/home/r2d2/brain"

    # Sync brain first
    subprocess.run(["bash", f"{brain_dir}/sync.sh"], capture_output=True, timeout=60)

    # Count skills and agents
    skills_count = len([d for d in os.listdir(f"{brain_dir}/skills")
                        if os.path.isdir(f"{brain_dir}/skills/{d}")]) if os.path.isdir(f"{brain_dir}/skills") else 0
    agents_count = len([d for d in os.listdir(f"{brain_dir}/agents")
                        if os.path.isdir(f"{brain_dir}/agents/{d}")]) if os.path.isdir(f"{brain_dir}/agents") else 0

    tag = f"brain-{month_str}"
    msg = f"Monthly brain snapshot — {month_str} | Skills: {skills_count} | Agents: {agents_count}"

    # Create annotated tag
    subprocess.run(["git", "-C", brain_dir, "tag", "-a", tag, "-m", msg], capture_output=True)
    result = subprocess.run(["git", "-C", brain_dir, "push", "origin", tag], capture_output=True, text=True)

    if result.returncode == 0:
        logger.info(f"MONTHLY TAG: pushed {tag} ✓")
        log["last_tag"] = month_str
        log["last_tag_time"] = now.isoformat()
        save_log(log)
    else:
        logger.error(f"MONTHLY TAG: push failed — {result.stderr.strip()}")


if __name__ == "__main__":
    # Force run for testing
    import logging
    logging.basicConfig(level=logging.INFO)
    from datetime import datetime
    now = datetime.now()
    month_str = now.strftime("%Y-%m")
    tag = f"brain-{month_str}"

    brain_dir = "/home/r2d2/brain"
    subprocess.run(["bash", f"{brain_dir}/sync.sh"])
    skills_count = len([d for d in os.listdir(f"{brain_dir}/skills") if os.path.isdir(f"{brain_dir}/skills/{d}")])
    agents_count = len([d for d in os.listdir(f"{brain_dir}/agents") if os.path.isdir(f"{brain_dir}/agents/{d}")])
    msg = f"Monthly brain snapshot — {month_str} | Skills: {skills_count} | Agents: {agents_count}"
    subprocess.run(["git", "-C", brain_dir, "tag", "-a", tag, "-m", msg])
    result = subprocess.run(["git", "-C", brain_dir, "push", "origin", tag], capture_output=True, text=True)
    print(f"Tag {tag}: {'✓' if result.returncode == 0 else result.stderr}")
