"""
OpenClaw Update Watcher — checks for new OpenClaw versions and asks Suhail.
"""

import subprocess
import json
import os
from datetime import datetime

STATE_FILE = "/home/r2d2/guardian/state.json"
CHECK_INTERVAL = 3600 * 6  # every 6 hours

def get_installed_version():
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            capture_output=True, text=True, timeout=10
        )
        # Parse version from output like "OpenClaw 2026.3.13"
        import re
        match = re.search(r'(\d{4}\.\d+\.\d+)', result.stdout + result.stderr)
        return match.group(1) if match else None
    except:
        return None

def get_latest_version():
    try:
        result = subprocess.run(
            ["npm", "view", "openclaw", "version"],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

def check_for_update():
    """Check if a new OpenClaw version is available. Returns (has_update, installed, latest)."""
    installed = get_installed_version()
    latest = get_latest_version()
    if not installed or not latest:
        return False, installed, latest
    # Normalize versions for comparison
    def normalize(v):
        return [int(x) for x in v.replace("-", ".").split(".")[:3] if x.isdigit()]
    try:
        has_update = normalize(latest) > normalize(installed)
        return has_update, installed, latest
    except:
        return False, installed, latest

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)

def run_update_check():
    state = load_state()
    now = datetime.now().timestamp()
    last_check = state.get("last_openclaw_check", 0)
    last_notified = state.get("last_openclaw_notified_version", "")

    if now - last_check < CHECK_INTERVAL:
        return  # Too soon

    state["last_openclaw_check"] = now
    save_state(state)

    has_update, installed, latest = check_for_update()

    if has_update and latest != last_notified:
        state["last_openclaw_notified_version"] = latest
        save_state(state)
        # Ask Suhail
        msg = (
            f"🆕 OpenClaw Update Available\n"
            f"Installed: {installed}\n"
            f"Latest: {latest}\n\n"
            f"Should I install it? Reply YES to update, or ignore to skip."
        )
        subprocess.run([
            "openclaw", "message", "send",
            "--channel", "whatsapp",
            "--target", "+14699941765",
            "--message", msg
        ], timeout=15, capture_output=True)

if __name__ == "__main__":
    has_update, installed, latest = check_for_update()
    print(f"Installed: {installed}")
    print(f"Latest: {latest}")
    print(f"Update available: {has_update}")
