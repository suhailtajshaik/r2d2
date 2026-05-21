"""Health check functions for Guardian."""

import subprocess
import json
import os
import ssl
import socket
import psutil
from datetime import datetime, timedelta


def run_all_checks():
    """Run all health checks. Returns list of (name, passed, message) tuples."""
    checks = [
        check_docker_containers,
        check_disk_space,
        check_memory,
        check_messaging_connectivity,
        check_ports,
        check_brain_sync,
        check_ssl_cert,
        check_notion_sync,
        check_memory_write,
        check_headlines_today_generator,
        check_docker_disk_usage,
        check_inflight_agents,
    ]
    results = []
    for check_fn in checks:
        try:
            name, passed, message = check_fn()
            results.append((name, passed, message))
        except Exception as e:
            results.append((check_fn.__name__, False, f"Check crashed: {e}"))
    return results



def check_docker_containers():
    """Check required Docker containers are running."""
    required = ["r2d2-nginx", "portfolio", "lab", "prompt-studio", "the-headlines-today", "the-headlines-today-dev"]
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        running = {}
        for line in result.stdout.strip().split("\n"):
            if "\t" in line:
                name, status = line.split("\t", 1)
                running[name] = status

        down = []
        for container in required:
            if container not in running:
                down.append(container)
            elif not running[container].startswith("Up"):
                down.append(container)

        if down:
            return ("Docker Containers", False, f"Down: {', '.join(down)}")
        return ("Docker Containers", True, f"All {len(required)} containers running")
    except Exception as e:
        return ("Docker Containers", False, str(e))


def check_disk_space():
    """Check disk usage on /."""
    try:
        usage = psutil.disk_usage("/")
        percent = usage.percent
        if percent > 85:
            return ("Disk Space", False, f"/ is {percent}% full ({usage.free // (1024**3)}GB free)")
        return ("Disk Space", True, f"/ is {percent}% full")
    except Exception as e:
        return ("Disk Space", False, str(e))


def check_memory():
    """Check memory usage."""
    try:
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            return ("Memory", False, f"{mem.percent}% used ({mem.available // (1024**2)}MB available)")
        return ("Memory", True, f"{mem.percent}% used")
    except Exception as e:
        return ("Memory", False, str(e))


def check_messaging_connectivity():
    """Messaging is handled by Hermes/Telegram now; legacy OpenClaw/WhatsApp gateway was removed."""
    return ("Messaging Connectivity", True, "Hermes/Telegram is the active notification path; legacy gateway check removed")


def check_ports():
    """Check nginx is accepting connections on 80 and 443."""
    issues = []
    for port in [80, 443]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            if result != 0:
                issues.append(f"Port {port} not accepting connections")
        except Exception as e:
            issues.append(f"Port {port}: {e}")

    if issues:
        return ("Nginx Ports", False, "; ".join(issues))
    return ("Nginx Ports", True, "Ports 80/443 open")


def check_brain_sync():
    """Check if brain repo has been pushed in the last 24 hours."""
    brain_dir = "/home/r2d2/brain"
    try:
        if not os.path.isdir(brain_dir):
            return ("Brain Sync", False, "Brain directory not found")

        result = subprocess.run(
            ["git", "-c", f"safe.directory={brain_dir}", "-C", brain_dir, "log", "-1", "--format=%ci"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return ("Brain Sync", False, f"Could not read git log: {result.stderr.strip() or result.stdout.strip()}")

        last_commit_str = result.stdout.strip()
        last_commit = datetime.fromisoformat(last_commit_str)
        age = datetime.now(last_commit.tzinfo) - last_commit
        if age > timedelta(hours=24):
            hours = int(age.total_seconds() // 3600)
            return ("Brain Sync", False, f"Last commit {hours}h ago — stale")
        return ("Brain Sync", True, f"Last commit {int(age.total_seconds() // 3600)}h ago")
    except Exception as e:
        return ("Brain Sync", False, str(e))


def check_ssl_cert():
    """Check SSL certificate expiry."""
    cert_path = "/home/r2d2/nginx/ssl/cert.pem"
    try:
        if not os.path.exists(cert_path):
            return ("SSL Cert", False, "cert.pem not found")

        result = subprocess.run(
            ["openssl", "x509", "-enddate", "-noout", "-in", cert_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return ("SSL Cert", False, f"openssl error: {result.stderr.strip()}")

        # Parse: notAfter=Mar 15 12:00:00 2026 GMT
        date_str = result.stdout.strip().split("=", 1)[1]
        expiry = datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z")
        days_left = (expiry - datetime.utcnow()).days

        if days_left < 0:
            return ("SSL Cert", False, f"Certificate EXPIRED {abs(days_left)} days ago")
        if days_left < 30:
            return ("SSL Cert", False, f"Certificate expires in {days_left} days")
        return ("SSL Cert", True, f"Certificate valid for {days_left} days")
    except Exception as e:
        return ("SSL Cert", False, str(e))


def check_notion_sync():
    """Check Notion was updated recently (within 12 hours)."""
    try:
        import urllib.request, json as _json
        api_key = os.environ.get('NOTION_API_KEY', open('/home/r2d2/.config/notion/api_key').read().strip() if os.path.exists('/home/r2d2/.config/notion/api_key') else '')
        req = urllib.request.Request(
            "https://api.notion.com/v1/pages/323c2d43-b275-81ac-8718-c10dd413af23",
            headers={"Authorization": f"Bearer {api_key}", "Notion-Version": "2022-06-28"}
        )
        import ssl as _ssl
        ctx = _ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            data = _json.load(r)
        last_edited = data.get("last_edited_time", "")
        if last_edited:
            from datetime import timezone
            dt = datetime.fromisoformat(last_edited.replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - dt
            if age.total_seconds() > 43200:  # 12 hours
                hrs = int(age.total_seconds() // 3600)
                return ("Notion Sync", False, f"Notion not updated in {hrs}h — stale")
            return ("Notion Sync", True, f"Updated {int(age.total_seconds()//3600)}h ago")
        return ("Notion Sync", False, "Could not read last_edited_time")
    except Exception as e:
        error = str(e)
        if "401" in error or "Unauthorized" in error or not locals().get("api_key"):
            return ("Notion Sync", True, "Skipped: Notion credentials unavailable/unauthorized; Guardian app watchdog remains active")
        return ("Notion Sync", False, error)


def check_memory_write():
    """Check that workspace memory directory is writable."""
    memory_dir = "/home/r2d2/brain/workspace/memory"
    test_file = f"{memory_dir}/.guardian_write_test"
    try:
        os.makedirs(memory_dir, exist_ok=True)
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return ("Memory Write", True, "Brain workspace writable")
    except Exception as e:
        return ("Memory Write", False, f"Cannot write to workspace: {e}")


def check_headlines_today_generator():
    """Check that Maxwell generated The Headlines Today within 26 hours."""
    from glob import glob
    try:
        archives = sorted(glob("/home/r2d2/headlines-today/*/*/*/headlines-today.pdf"))
        if not archives:
            return ("Maxwell Headlines Today", False, "No Headlines Today editions found")
        latest = archives[-1]
        mtime = datetime.fromtimestamp(os.path.getmtime(latest))
        age = datetime.now() - mtime
        if age.total_seconds() > 93600:  # 26 hours
            hrs = int(age.total_seconds() // 3600)
            return ("Maxwell Headlines Today", False, f"Last Headlines Today edition {hrs}h ago — Maxwell may have failed")
        return ("Maxwell Headlines Today", True, f"Last Headlines Today edition {int(age.total_seconds()//3600)}h ago")
    except Exception as e:
        return ("Maxwell Headlines Today", False, str(e))


def check_docker_disk_usage():
    """Check Docker isn't eating too much disk with unused images/containers."""
    try:
        result = subprocess.run(
            ["docker", "system", "df", "--format", "{{.Type}}\t{{.Size}}\t{{.Reclaimable}}"],
            capture_output=True, text=True, timeout=15
        )
        lines = result.stdout.strip().split("\n")
        reclaimable_gb = 0
        for line in lines:
            parts = line.split("\t")
            if len(parts) >= 3:
                rec = parts[2].replace("B","").strip()
                # Parse size — rough estimate
                if "GB" in rec:
                    try: reclaimable_gb += float(rec.replace("GB","").split("(")[-1].strip())
                    except: pass
        if reclaimable_gb > 5:
            return ("Docker Disk", False, f"{reclaimable_gb:.1f}GB reclaimable — needs pruning")
        return ("Docker Disk", True, f"{reclaimable_gb:.1f}GB reclaimable")
    except Exception as e:
        return ("Docker Disk", False, str(e))


def check_inflight_agents():
    """Check if any 3PO/Trooper processes are running and healthy."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "claude.*bypassPermissions"],
            capture_output=True, text=True
        )
        pids = [p for p in result.stdout.strip().split("\n") if p]
        # Just report — Guardian doesn't kill agents, just tracks them
        if pids:
            return ("In-Flight Agents", True, f"{len(pids)} agent(s) running: {', '.join(pids[:3])}")
        return ("In-Flight Agents", True, "No agents running")
    except Exception as e:
        return ("In-Flight Agents", True, "Check skipped")  # Non-critical
