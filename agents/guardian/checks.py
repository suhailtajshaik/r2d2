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
        check_openclaw_gateway,
        check_docker_containers,
        check_disk_space,
        check_memory,
        check_whatsapp_connectivity,
        check_ports,
        check_brain_sync,
        check_ssl_cert,
        check_notion_sync,
        check_memory_write,
        check_newspaper_generator,
    ]
    results = []
    for check_fn in checks:
        try:
            name, passed, message = check_fn()
            results.append((name, passed, message))
        except Exception as e:
            results.append((check_fn.__name__, False, f"Check crashed: {e}"))
    return results


def check_openclaw_gateway():
    """Check OpenClaw gateway health."""
    try:
        result = subprocess.run(
            ["openclaw", "health", "--json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return ("OpenClaw Gateway", False, f"Health check failed: {result.stderr.strip()}")
        data = json.loads(result.stdout)
        status = data.get("status", "unknown")
        if status == "healthy":
            return ("OpenClaw Gateway", True, "Healthy")
        return ("OpenClaw Gateway", False, f"Status: {status}")
    except subprocess.TimeoutExpired:
        return ("OpenClaw Gateway", False, "Health check timed out")
    except json.JSONDecodeError:
        return ("OpenClaw Gateway", False, "Invalid JSON response")
    except FileNotFoundError:
        return ("OpenClaw Gateway", False, "openclaw CLI not found")
    except Exception as e:
        return ("OpenClaw Gateway", False, str(e))


def check_docker_containers():
    """Check required Docker containers are running."""
    required = ["r2d2-nginx", "portfolio", "lab", "prompt-studio", "news-site"]
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


def check_whatsapp_connectivity():
    """Check WhatsApp by verifying OpenClaw gateway is reachable on its port."""
    import socket
    try:
        # Check if OpenClaw gateway port is open (18789)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("127.0.0.1", 18789))
        sock.close()
        if result == 0:
            return ("WhatsApp Connectivity", True, "Gateway port reachable")
        return ("WhatsApp Connectivity", False, "Gateway port 18789 not reachable")
    except Exception as e:
        return ("WhatsApp Connectivity", False, str(e))


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
            ["git", "-C", brain_dir, "log", "-1", "--format=%ci"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return ("Brain Sync", False, "Could not read git log")

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
        return ("Notion Sync", False, str(e))


def check_memory_write():
    """Check that workspace memory directory is writable."""
    memory_dir = "/home/r2d2/.openclaw/workspace/memory"
    test_file = f"{memory_dir}/.guardian_write_test"
    try:
        os.makedirs(memory_dir, exist_ok=True)
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return ("Memory Write", True, "Workspace writable")
    except Exception as e:
        return ("Memory Write", False, f"Cannot write to workspace: {e}")


def check_newspaper_generator():
    """Check that last newspaper was generated within 26 hours."""
    from glob import glob
    try:
        archives = sorted(glob("/home/r2d2/newspapers/*/*/*/headlines-today.pdf"))
        if not archives:
            return ("Newspaper Generator", False, "No newspaper archives found")
        latest = archives[-1]
        mtime = datetime.fromtimestamp(os.path.getmtime(latest))
        age = datetime.now() - mtime
        if age.total_seconds() > 93600:  # 26 hours
            hrs = int(age.total_seconds() // 3600)
            return ("Newspaper Generator", False, f"Last newspaper {hrs}h ago — may have failed")
        return ("Newspaper Generator", True, f"Last newspaper {int(age.total_seconds()//3600)}h ago")
    except Exception as e:
        return ("Newspaper Generator", False, str(e))
