"""Auto-heal functions for Guardian."""

import subprocess
import logging
import os

log = logging.getLogger("guardian.healer")


def attempt_heal(check_name, message):
    """Try to auto-heal a known issue. Returns True if healed."""
    heal_map = {
        "Docker Containers": heal_docker_containers,
        "Nginx Ports": heal_nginx,
        "Disk Space": heal_disk_space,
        "OpenClaw Gateway": heal_openclaw,
        "Notion Sync": heal_notion_sync,
        "Memory Write": heal_memory_write,
        "Newspaper Generator": heal_newspaper_generator,
    }
    heal_fn = heal_map.get(check_name)
    if heal_fn is None:
        log.info(f"No auto-heal for: {check_name}")
        return False
    try:
        return heal_fn(message)
    except Exception as e:
        log.error(f"Heal failed for {check_name}: {e}")
        return False


def heal_docker_containers(message):
    """Restart stopped containers."""
    if not message.startswith("Down: "):
        return False

    containers = [c.strip() for c in message[6:].split(",")]
    all_started = True
    for container in containers:
        log.info(f"Starting container: {container}")
        result = subprocess.run(
            ["docker", "start", container],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            log.error(f"Failed to start {container}: {result.stderr.strip()}")
            all_started = False
        else:
            log.info(f"Started {container}")
    return all_started


def heal_nginx(message):
    """Try to restart nginx container if ports are down."""
    log.info("Attempting nginx restart")
    result = subprocess.run(
        ["docker", "restart", "r2d2-nginx"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        log.info("Nginx restarted successfully")
        return True
    log.error(f"Nginx restart failed: {result.stderr.strip()}")
    return False


def heal_disk_space(message):
    """Clean up docker images and logs."""
    log.info("Cleaning up disk space")
    subprocess.run(
        ["docker", "system", "prune", "-f"],
        capture_output=True, text=True, timeout=60
    )
    subprocess.run(
        ["find", "/var/log", "-name", "*.log", "-size", "+100M", "-exec", "truncate", "-s", "0", "{}", ";"],
        capture_output=True, text=True, timeout=30
    )
    log.info("Disk cleanup complete")
    return True


def heal_openclaw(message):
    """Restart OpenClaw gateway."""
    log.info("Restarting OpenClaw gateway")
    result = subprocess.run(
        ["openclaw", "gateway", "restart"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        log.info("OpenClaw gateway restarted")
        return True
    log.error(f"OpenClaw restart failed: {result.stderr.strip()}")
    return False


def call_3po(issue_description):
    """Spawn Claude Code to diagnose and fix a complex issue."""
    log.info(f"Calling 3PO for: {issue_description}")
    prompt = f"""You are R2D2's repair agent on VPS srv1305247.

ISSUE DETECTED: {issue_description}

Diagnose and fix the issue. You have full access to the VPS.
Key paths:
- OpenClaw: /home/r2d2/.openclaw/
- Nginx: /home/r2d2/nginx/
- Projects: /home/r2d2/projects/
- Brain: /home/r2d2/brain/

After fixing, verify the fix works.
Then notify Suhail: openclaw message send --channel whatsapp --target +14699941765 --message "3PO fixed: {issue_description}"
"""
    # Drop to r2d2 user since Claude Code refuses bypassPermissions as root
    subprocess.Popen(
        ["su", "-", "r2d2", "-c",
         f"claude --permission-mode bypassPermissions --print '{prompt.replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'"],
        env={**os.environ, "HOME": "/home/r2d2"}
    )


def heal_notion_sync(message):
    """Call 3PO to update Notion."""
    call_3po("Notion sync is stale. Update all Notion pages (Session Log, VPS State) with current system status. Use the Notion API key at ~/.config/notion/api_key")
    return False  # 3PO handles it

def heal_memory_write(message):
    """Fix workspace write permissions."""
    import subprocess
    subprocess.run(["chmod", "-R", "755", "/home/r2d2/.openclaw/workspace/memory"])
    subprocess.run(["chmod", "700", "/home/r2d2/.openclaw/credentials"])
    return True

def heal_newspaper_generator(message):
    """Call 3PO to regenerate newspaper."""
    call_3po("The newspaper generator may have failed. Run: python3 /home/r2d2/tools/generate-newspaper.py — and fix any errors.")
    return False


# Extended heal dispatch
HEAL_MAP_EXTENDED = {
    "Notion Sync": heal_notion_sync,
    "Memory Write": heal_memory_write,
    "Newspaper Generator": heal_newspaper_generator,
}


def research_and_fix_permanently(check_name, history):
    """
    Dispatch 3PO to research the root cause of a recurring issue
    and apply a permanent fix, not just a band-aid.
    """
    messages = history.get("messages", [])
    count = history.get("count", 0)
    first_seen = history.get("first_seen", "unknown")

    prompt = f"""You are Guardian's permanent fix agent on VPS srv1305247.

RECURRING ISSUE: {check_name}
Occurrences: {count} times since {first_seen}
Error messages seen: {json.dumps(messages, indent=2)}

This issue keeps coming back. Your job is NOT to patch it again — find and fix the ROOT CAUSE permanently.

Steps:
1. Research the issue — check logs, configs, systemd units, docker configs
2. Search the web if needed: python3 /home/r2d2/tools/websearch.py --summary "<issue> permanent fix"
3. Identify WHY it keeps happening (misconfiguration, missing dependency, race condition, etc.)
4. Apply a permanent fix (update config, add restart policy, fix permissions, etc.)
5. Verify the fix works
6. Document what you did in /home/r2d2/guardian/knowledge.json under permanent_fixes.{check_name.replace(' ','_')}
7. Send Suhail a brief WhatsApp: openclaw message send --channel whatsapp --target +14699941765 --message "🔧 Guardian permanently fixed: {check_name}\\n[brief explanation of root cause and fix]"

Be thorough. This must not happen again.
"""
    import subprocess
    subprocess.Popen([
        "claude", "--permission-mode", "bypassPermissions", "--print", prompt
    ])
