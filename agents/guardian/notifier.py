"""
Guardian Notifier — Suhail only gets pinged when he needs to act or must know.
Silent on everything else.
"""

import subprocess
import os
import json
from datetime import datetime

PHONE = os.environ.get("GUARDIAN_PHONE", "+14699941765")
CHANNEL = os.environ.get("GUARDIAN_CHANNEL", "whatsapp")
STATE_FILE = "/home/r2d2/guardian/state.json"

# How long to wait before re-alerting the same issue (seconds)
REALERT_COOLDOWN = 3600  # 1 hour

def _load_alert_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}

def _save_alert_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)

def _send(message):
    """Send WhatsApp message to Suhail."""
    try:
        subprocess.run([
            "openclaw", "message", "send",
            "--channel", CHANNEL,
            "--target", PHONE,
            "--message", message
        ], timeout=15, capture_output=True)
    except Exception as e:
        pass  # If we can't notify, log it silently

def notify_needs_action(issue, detail):
    """
    Notify Suhail ONLY when something needs his attention that
    Guardian + 3PO cannot fix automatically.
    Examples: credentials expired, billing issue, manual config needed.
    """
    state = _load_alert_state()
    alerts = state.get("alerts_sent", {})
    now = datetime.now().timestamp()

    # Don't re-alert within cooldown period
    if issue in alerts:
        last_sent = alerts[issue]
        if now - last_sent < REALERT_COOLDOWN:
            return

    alerts[issue] = now
    state["alerts_sent"] = alerts
    _save_alert_state(state)

    _send(f"🚨 Guardian — Action Required\n*{issue}*\n{detail}\n\nGuardian + 3PO could not fix this automatically.")

def notify_critical(issue, detail):
    """
    Notify Suhail about critical issues he must know about,
    even if being auto-fixed (e.g. site was down, now recovering).
    """
    state = _load_alert_state()
    alerts = state.get("alerts_sent", {})
    now = datetime.now().timestamp()

    if issue in alerts:
        if now - alerts[issue] < REALERT_COOLDOWN:
            return

    alerts[issue] = now
    state["alerts_sent"] = alerts
    _save_alert_state(state)

    _send(f"⚠️ Guardian — FYI\n*{issue}*\n{detail}\n\nHandling it now.")

def notify_resolved(issue):
    """
    Notify Suhail ONLY if a previously alerted issue is now resolved.
    Silent if the issue was never alerted.
    """
    state = _load_alert_state()
    alerts = state.get("alerts_sent", {})

    if issue not in alerts:
        return  # Never told him about it — don't bother

    del alerts[issue]
    state["alerts_sent"] = alerts
    _save_alert_state(state)

    _send(f"✅ Guardian — Fixed\n*{issue}* is back to normal.")

# Legacy compatibility — used in guardian.py
def notify(message, urgent=False):
    """
    Legacy notify. Only sends if urgent=True AND it's truly critical.
    Startup messages and auto-heals are suppressed.
    """
    if not urgent:
        return  # Silent — Suhail doesn't need routine updates
    
    # Even urgent: suppress known auto-healable patterns
    suppress_patterns = [
        "Guardian online",
        "Guardian starting",
        "Auto-fixed",
        "Recovered:",
        "Calling 3PO",
    ]
    for pattern in suppress_patterns:
        if pattern in message:
            return  # 3PO handles it — no need to ping Suhail

    _send(message)
