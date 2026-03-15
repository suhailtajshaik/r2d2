"""
Guardian v3 — Self-learning watchdog for R2D2.
- Monitors everything every 60s
- Auto-heals simple issues
- Calls 3PO for complex issues
- Researches ROOT CAUSE for recurring issues — fixes permanently
- Checks for OpenClaw updates every 6h — asks Suhail before installing
- Silent unless Suhail needs to act
"""

import time
import json
import os
import logging
from datetime import datetime

from checks import run_all_checks
from healer import attempt_heal, call_3po, research_and_fix_permanently
from notifier import notify_needs_action, notify_critical, notify_resolved
from learner import record_issue, should_research_permanent_fix, get_issue_history, is_root_fixed
from openclaw_watcher import run_update_check
from skill_evolver import run_skill_evolution
from brain_consolidator import run_brain_consolidation
from monthly_tagger import run_monthly_tag

STATE_FILE = "/home/r2d2/guardian/state.json"
CHECK_INTERVAL = 60

NEEDS_HUMAN = [
    "SSL Cert",
    "WhatsApp Connectivity",
]

TELL_SUHAIL_IF_PERSISTENT = [
    "OpenClaw Gateway",
    "Docker Containers",
    "Nginx Ports",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/home/r2d2/guardian/logs/guardian.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("guardian")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            try:
                return json.load(f)
            except:
                pass
    return {"issues": {}, "alerts_sent": {}, "start_time": datetime.now().isoformat()}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)

def main():
    os.makedirs("/home/r2d2/guardian/logs", exist_ok=True)
    log.info("Guardian v3 starting — self-learning mode active")

    state = load_state()

    while True:
        try:
            # --- Health Checks ---
            results = run_all_checks()
            for check_name, passed, message in results:

                if passed:
                    if check_name in state.get("issues", {}):
                        log.info(f"RECOVERED: {check_name}")
                        notify_resolved(check_name)
                        del state["issues"][check_name]
                else:
                    # Record for learning
                    total_count = record_issue(check_name, message)

                    if check_name not in state.get("issues", {}):
                        state.setdefault("issues", {})[check_name] = {
                            "since": datetime.now().isoformat(),
                            "attempts": 0
                        }
                        log.warning(f"ISSUE [{total_count}x total]: {check_name} — {message}")

                        # Try auto-heal first
                        healed = attempt_heal(check_name, message)
                        if healed:
                            log.info(f"AUTO-HEALED: {check_name}")
                            del state["issues"][check_name]
                            continue

                        # Needs human?
                        if check_name in NEEDS_HUMAN:
                            notify_needs_action(check_name, message)
                        else:
                            # Check if this is recurring — research permanent fix
                            if should_research_permanent_fix(check_name, threshold=3) and not is_root_fixed(check_name):
                                log.warning(f"RECURRING ({total_count}x) — dispatching 3PO for permanent fix: {check_name}")
                                history = get_issue_history(check_name)
                                research_and_fix_permanently(check_name, history)
                            else:
                                # Normal 3PO dispatch
                                call_3po(f"{check_name}: {message}")

                    else:
                        state["issues"][check_name]["attempts"] = state["issues"][check_name].get("attempts", 0) + 1
                        attempts = state["issues"][check_name]["attempts"]

                        if attempts == 3 and check_name in TELL_SUHAIL_IF_PERSISTENT:
                            notify_critical(check_name, f"{message}\n3PO is working on a permanent fix.")

                        # Every 10 cycles still broken — try permanent fix research
                        if attempts % 10 == 0 and check_name not in NEEDS_HUMAN:
                            if not is_root_fixed(check_name):
                                log.warning(f"STILL BROKEN ({attempts} cycles) — escalating to permanent fix research")
                                history = get_issue_history(check_name)
                                research_and_fix_permanently(check_name, history)

            save_state(state)

            # --- OpenClaw Update Check (every 6h) ---
            try:
                run_update_check()
            except Exception as e:
                log.error(f"Update check error: {e}")

            # --- Skill Evolution (1 skill per day, staggered weekly cycle) ---
            try:
                run_skill_evolution()
            except Exception as e:
                log.error(f"Skill evolution error: {e}")

            # --- Brain Consolidation (daily — compress, distill, strengthen) ---
            try:
                run_brain_consolidation()
            except Exception as e:
                log.error(f"Brain consolidation error: {e}")

            # --- Monthly Brain Tag (1st of month) ---
            try:
                run_monthly_tag()
            except Exception as e:
                log.error(f"Monthly tag error: {e}")

        except Exception as e:
            log.error(f"Guardian loop error: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
