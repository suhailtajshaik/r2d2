"""
Guardian Learner — tracks recurring issues and fixes them permanently.
If the same issue fires 3+ times, 3PO researches a root cause fix.
"""

import json
import os
from datetime import datetime

KNOWLEDGE_FILE = "/home/r2d2/guardian/knowledge.json"

def load_knowledge():
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE) as f:
            try:
                return json.load(f)
            except:
                pass
    return {"recurring": {}, "permanent_fixes": {}, "open_issues": []}

def save_knowledge(k):
    with open(KNOWLEDGE_FILE, "w") as f:
        json.dump(k, f, indent=2, default=str)

def record_issue(check_name, message):
    """Track how many times an issue has occurred."""
    k = load_knowledge()
    r = k.setdefault("recurring", {})
    if check_name not in r:
        r[check_name] = {"count": 0, "first_seen": datetime.now().isoformat(), "messages": [], "root_fixed": False}
    r[check_name]["count"] += 1
    r[check_name]["last_seen"] = datetime.now().isoformat()
    if message not in r[check_name]["messages"]:
        r[check_name]["messages"].append(message)
    save_knowledge(k)
    return r[check_name]["count"]

def is_root_fixed(check_name):
    k = load_knowledge()
    return k.get("recurring", {}).get(check_name, {}).get("root_fixed", False)

def mark_root_fixed(check_name, fix_description):
    k = load_knowledge()
    k["recurring"].setdefault(check_name, {})["root_fixed"] = True
    k["recurring"][check_name]["fix_description"] = fix_description
    k["recurring"][check_name]["fixed_at"] = datetime.now().isoformat()
    k["permanent_fixes"][check_name] = {
        "description": fix_description,
        "applied_at": datetime.now().isoformat()
    }
    save_knowledge(k)

def should_research_permanent_fix(check_name, threshold=3):
    """Returns True if issue has recurred enough to warrant a permanent fix."""
    k = load_knowledge()
    count = k.get("recurring", {}).get(check_name, {}).get("count", 0)
    already_fixed = k.get("recurring", {}).get(check_name, {}).get("root_fixed", False)
    return count >= threshold and not already_fixed

def get_issue_history(check_name):
    k = load_knowledge()
    return k.get("recurring", {}).get(check_name, {})
