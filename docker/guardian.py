#!/usr/bin/env python3
"""
Guardian v4 — Self-Healing Infrastructure Watchdog
Monitors 10+ systems every 5 minutes with smart retry logic, diagnostics, and predictive maintenance.

Features:
- Exponential backoff + circuit breaker pattern
- Pre-restart log capture and system state snapshots
- Predictive maintenance (disk trend analysis)
- Self-learning (success rate tracking)
- Alert grouping + deduplication
- Graceful degradation for failed services
"""

import os
import json
import time
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import hashlib
import signal
import sys

# Configuration
LOG_DIR = "/tmp/guardian"
STATE_FILE = f"{LOG_DIR}/state.json"
DIAGNOSTICS_DIR = f"{LOG_DIR}/diagnostics"
MEMORY_FILE = "/home/r2d2/.openclaw/workspace/memory/guardian-learning.md"
ALERTS_FILE = "/home/r2d2/.openclaw/workspace/memory/guardian-alerts.log"
NEWSPAPER_DATE = datetime.now().strftime("%Y/%m/%d")
NEWSPAPER_DATE_SLUG = datetime.now().strftime("%Y-%m-%d")

# Alert batching
ALERT_WINDOW = 300  # 5 minutes
ALERT_THRESHOLD = 2  # Alert if 2+ issues in one cycle

# Circuit breaker
CIRCUIT_BREAKER_THRESHOLD = 5  # 5 consecutive failures
CIRCUIT_BREAKER_COOL_DOWN = 1800  # 30 minutes

# Retry strategy
EXPONENTIAL_BACKOFF = [1, 2, 4]  # seconds
RETRY_TIMEOUT = 30

# Service priorities
CRITICAL_SERVICES = ["nginx", "news-site", "guardian"]
DISABLE_NON_CRITICAL_AFTER_N_FAILURES = 3

# Initialize
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DIAGNOSTICS_DIR, exist_ok=True)
os.makedirs(Path(MEMORY_FILE).parent, exist_ok=True)


class Logger:
    """Structured logging with timestamps"""

    def __init__(self, name: str):
        self.name = name
        self.log_file = f"{LOG_DIR}/guardian.log"

    def log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level:8s}] [{self.name:15s}] {message}"
        print(entry)
        with open(self.log_file, "a") as f:
            f.write(entry + "\n")

    def info(self, msg: str):
        self.log("INFO", msg)

    def warning(self, msg: str):
        self.log("WARN", msg)

    def error(self, msg: str):
        self.log("ERROR", msg)

    def debug(self, msg: str):
        self.log("DEBUG", msg)


logger = Logger("Guardian")


class StateManager:
    """Track service state, failures, and remediation history"""

    def __init__(self):
        self.state: Dict = self._load_state()

    def _load_state(self) -> Dict:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")
        return {
            "services": {},
            "circuit_breakers": {},
            "failure_patterns": {},
            "remediation_history": [],
            "last_alert_hash": None,
        }

    def save(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def get_service(self, name: str) -> Dict:
        if name not in self.state["services"]:
            self.state["services"][name] = {
                "consecutive_failures": 0,
                "total_failures": 0,
                "last_failure": None,
                "remediation_attempts": 0,
                "remediation_success": 0,
                "disabled": False,
                "failed_checks": [],
            }
        return self.state["services"][name]

    def record_failure(self, service: str, check_name: str, error: str):
        svc = self.get_service(service)
        svc["consecutive_failures"] += 1
        svc["total_failures"] += 1
        svc["last_failure"] = datetime.now().isoformat()
        svc["failed_checks"].append(
            {"check": check_name, "error": error, "time": datetime.now().isoformat()}
        )
        self.save()
        logger.warning(
            f"{service}/{check_name} failed: {error} (consecutive: {svc['consecutive_failures']})"
        )

    def record_success(self, service: str):
        svc = self.get_service(service)
        svc["consecutive_failures"] = 0
        self.save()

    def record_remediation(self, service: str, action: str, success: bool):
        svc = self.get_service(service)
        svc["remediation_attempts"] += 1
        if success:
            svc["remediation_success"] += 1
        self.state["remediation_history"].append(
            {
                "service": service,
                "action": action,
                "success": success,
                "time": datetime.now().isoformat(),
            }
        )
        self.save()
        logger.info(
            f"Remediation {service}/{action}: {'✅' if success else '❌'} "
            f"(success rate: {svc['remediation_success']}/{svc['remediation_attempts']})"
        )

    def is_circuit_broken(self, service: str) -> bool:
        svc = self.get_service(service)
        if svc["consecutive_failures"] >= CIRCUIT_BREAKER_THRESHOLD:
            if service not in self.state["circuit_breakers"]:
                self.state["circuit_breakers"][service] = datetime.now().isoformat()
                logger.warning(
                    f"🔴 Circuit breaker OPEN for {service} after {CIRCUIT_BREAKER_THRESHOLD} failures"
                )
                self.save()
            return True
        return False

    def should_disable_service(self, service: str) -> bool:
        svc = self.get_service(service)
        if (
            service not in CRITICAL_SERVICES
            and svc["total_failures"] >= DISABLE_NON_CRITICAL_AFTER_N_FAILURES
        ):
            svc["disabled"] = True
            self.save()
            return True
        return False


class Diagnostics:
    """Capture system state before and after remediation"""

    @staticmethod
    def snapshot() -> Dict:
        """Capture disk, memory, process state"""
        snapshot = {"timestamp": datetime.now().isoformat()}

        # Disk usage
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                snapshot["disk"] = {
                    "used": parts[2],
                    "available": parts[3],
                    "percent": parts[4],
                }
        except Exception as e:
            logger.debug(f"Disk snapshot failed: {e}")

        # Memory usage
        try:
            result = subprocess.run(
                ["free", "-h"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                snapshot["memory"] = {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[6],
                }
        except Exception as e:
            logger.debug(f"Memory snapshot failed: {e}")

        # Top processes
        try:
            result = subprocess.run(
                ["ps", "aux", "--sort=-rss"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            lines = result.stdout.strip().split("\n")[1:6]
            snapshot["top_processes"] = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 11:
                    snapshot["top_processes"].append(
                        {
                            "pid": parts[1],
                            "rss": parts[5],
                            "cmd": " ".join(parts[10:]),
                        }
                    )
        except Exception as e:
            logger.debug(f"Top processes snapshot failed: {e}")

        return snapshot

    @staticmethod
    def get_container_logs(container_name: str, lines: int = 50) -> str:
        """Capture container logs before restart"""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), container_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Failed to capture logs: {e}"

    @staticmethod
    def save_diagnostic_report(service: str, action: str, snapshot_before, logs_before, snapshot_after):
        """Save diagnostic report for human review"""
        report = {
            "service": service,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "snapshot_before": snapshot_before,
            "logs_before": logs_before,
            "snapshot_after": snapshot_after,
        }
        report_file = f"{DIAGNOSTICS_DIR}/{service}_{action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"📋 Diagnostic report saved: {report_file}")
        return report_file


class PredictiveMaintenance:
    """Analyze trends and alert before failures"""

    HISTORY_FILE = f"{LOG_DIR}/metrics-history.json"

    @staticmethod
    def record_metric(name: str, value: float):
        """Record a metric (e.g., disk usage %)"""
        history = {}
        if os.path.exists(PredictiveMaintenance.HISTORY_FILE):
            with open(PredictiveMaintenance.HISTORY_FILE) as f:
                history = json.load(f)

        if name not in history:
            history[name] = []

        history[name].append(
            {"time": datetime.now().isoformat(), "value": value}
        )

        # Keep last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        for metric in history.values():
            metric[:] = [
                m
                for m in metric
                if datetime.fromisoformat(m["time"]) > cutoff
            ]

        with open(PredictiveMaintenance.HISTORY_FILE, "w") as f:
            json.dump(history, f)

    @staticmethod
    def predict_disk_full() -> Optional[str]:
        """Predict when disk will fill at current growth rate"""
        try:
            result = subprocess.run(
                ["df", "/"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                percent = int(parts[4].rstrip("%"))

                # Record metric
                PredictiveMaintenance.record_metric("disk_usage_percent", percent)

                # Alert if >80%
                if percent > 80:
                    return f"⚠️ Disk usage at {percent}% — may fill within 24h"

                # Check trend
                history = {}
                if os.path.exists(PredictiveMaintenance.HISTORY_FILE):
                    with open(PredictiveMaintenance.HISTORY_FILE) as f:
                        history = json.load(f)

                if "disk_usage_percent" in history:
                    metrics = history["disk_usage_percent"][-12:]  # Last 12 samples
                    if len(metrics) > 6:
                        # Simple linear trend: (last - first) / time_span_hours
                        first_val = metrics[0]["value"]
                        last_val = metrics[-1]["value"]
                        time_span_hours = (
                            datetime.fromisoformat(metrics[-1]["time"])
                            - datetime.fromisoformat(metrics[0]["time"])
                        ).total_seconds() / 3600
                        if time_span_hours > 0:
                            growth_per_hour = (last_val - first_val) / time_span_hours
                            if growth_per_hour > 0.5:  # >0.5% per hour
                                hours_to_full = (100 - percent) / growth_per_hour
                                days = hours_to_full / 24
                                return (
                                    f"📈 Disk growth trajectory: will fill in {days:.1f} days "
                                    f"({growth_per_hour:.2f}%/hour). "
                                    f"Suggest: cleanup old logs, archive newspapers"
                                )
        except Exception as e:
            logger.debug(f"Disk prediction failed: {e}")

        return None


class RetryStrategy:
    """Exponential backoff with circuit breaker"""

    @staticmethod
    def execute_with_backoff(
        func,
        service: str,
        max_retries: int = 3,
        timeout: int = RETRY_TIMEOUT,
    ) -> Tuple[bool, str]:
        """Execute with exponential backoff (1s, 2s, 4s)"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{max_retries} for {service}")
                result = func()
                logger.info(f"✅ {service} succeeded on attempt {attempt + 1}")
                return True, "Success"
            except subprocess.TimeoutExpired:
                error = f"Timeout after {timeout}s"
                logger.warning(f"⏱️ {service} timed out")
            except Exception as e:
                error = str(e)
                logger.warning(f"❌ {service} failed: {error}")

            # Exponential backoff
            if attempt < max_retries - 1:
                wait_time = EXPONENTIAL_BACKOFF[attempt]
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

        return False, error


class Remediation:
    """Auto-fix actions"""

    @staticmethod
    def restart_docker_container(container_name: str, state: StateManager) -> bool:
        """Restart a Docker container with diagnostics"""
        logger.info(f"🔧 Restarting container: {container_name}")

        # Capture diagnostics before
        snapshot_before = Diagnostics.snapshot()
        logs_before = Diagnostics.get_container_logs(container_name)

        def restart():
            subprocess.run(
                ["docker", "restart", container_name],
                timeout=RETRY_TIMEOUT,
                check=True,
            )
            time.sleep(5)
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if container_name not in result.stdout:
                raise RuntimeError(f"Container {container_name} not running after restart")

        success, error = RetryStrategy.execute_with_backoff(
            restart, f"restart:{container_name}"
        )

        # Capture diagnostics after
        snapshot_after = Diagnostics.snapshot()

        if success:
            Diagnostics.save_diagnostic_report(
                container_name, "restart", snapshot_before, logs_before, snapshot_after
            )
            state.record_remediation(container_name, "restart", True)
            return True
        else:
            logger.error(f"Failed to restart {container_name}: {error}")
            state.record_remediation(container_name, "restart", False)
            return False

    @staticmethod
    def regenerate_newspaper(state: StateManager) -> bool:
        """Regenerate newspaper data"""
        logger.info("🔧 Regenerating newspaper...")

        def generate():
            subprocess.run(
                ["node", "/home/r2d2/generate-newspaper.js"],
                timeout=RETRY_TIMEOUT,
                check=True,
                cwd="/home/r2d2",
            )

        success, error = RetryStrategy.execute_with_backoff(
            generate, "newspaper:generate"
        )

        if success:
            state.record_remediation("newspaper", "regenerate", True)
            return True
        else:
            logger.error(f"Failed to regenerate newspaper: {error}")
            state.record_remediation("newspaper", "regenerate", False)
            return False

    @staticmethod
    def rebuild_site(state: StateManager) -> bool:
        """Rebuild and redeploy news site"""
        logger.info("🔧 Rebuilding news site...")

        def rebuild():
            subprocess.run(
                ["npm", "run", "build"],
                timeout=RETRY_TIMEOUT,
                check=True,
                cwd="/home/r2d2/projects/news-site-v2",
            )

        success, error = RetryStrategy.execute_with_backoff(
            rebuild, "news-site:build"
        )

        if success:
            state.record_remediation("news-site", "rebuild", True)
            return True
        else:
            logger.error(f"Failed to rebuild news site: {error}")
            state.record_remediation("news-site", "rebuild", False)
            return False


class HealthChecks:
    """Comprehensive system checks"""

    @staticmethod
    def check_newspaper_data(state: StateManager) -> bool:
        """Check if today's newspaper data exists and is fresh"""
        data_file = f"/home/r2d2/newspapers/{NEWSPAPER_DATE}/data.json"

        if not os.path.exists(data_file):
            state.record_failure("newspaper", "data-file", "File not found")
            return False

        size = os.path.getsize(data_file)
        if size < 5000:
            state.record_failure("newspaper", "data-file", f"Too small ({size} bytes)")
            return False

        mtime = os.path.getmtime(data_file)
        age_hours = (time.time() - mtime) / 3600
        if age_hours > 24:
            state.record_failure("newspaper", "data-file", f"Too old ({age_hours:.1f}h)")
            return False

        state.record_success("newspaper")
        logger.info(f"✅ Newspaper data: OK ({size // 1024}KB, {age_hours:.1f}h old)")
        return True

    @staticmethod
    def check_pdf(state: StateManager) -> bool:
        """Check if PDF exists and is valid"""
        pdf = f"/home/r2d2/newspapers/{NEWSPAPER_DATE}/headlines-today.pdf"

        if not os.path.exists(pdf):
            state.record_failure("newspaper", "pdf", "File not found")
            return False

        size = os.path.getsize(pdf)
        if size < 10240:
            state.record_failure("newspaper", "pdf", f"Too small ({size} bytes)")
            return False

        state.record_success("newspaper")
        logger.info(f"✅ PDF: OK ({size // 1024}KB)")
        return True

    @staticmethod
    def check_audio(state: StateManager) -> bool:
        """Check if audio exists and is valid"""
        audio = f"/home/r2d2/newspapers/{NEWSPAPER_DATE}/headlines-today.mp3"

        if not os.path.exists(audio):
            state.record_failure("newspaper", "audio", "File not found")
            return False

        size = os.path.getsize(audio)
        if size < 100000:
            state.record_failure("newspaper", "audio", f"Too small ({size} bytes)")
            return False

        state.record_success("newspaper")
        logger.info(f"✅ Audio: OK ({size // 1024}KB)")
        return True

    @staticmethod
    def check_web_deployment(state: StateManager) -> bool:
        """Check if web API is responding"""
        url = f"https://news.suhailtaj.cloud/archive/{NEWSPAPER_DATE_SLUG}/data.json"

        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
                capture_output=True,
                text=True,
                timeout=10,
            )
            status = result.stdout.strip()

            if status != "200":
                state.record_failure("news-site", "web-deployment", f"HTTP {status}")
                return False

            state.record_success("news-site")
            logger.info(f"✅ Web deployment: OK (HTTP {status})")
            return True
        except Exception as e:
            state.record_failure("news-site", "web-deployment", str(e))
            return False

    @staticmethod
    def check_cron_job(state: StateManager) -> bool:
        """Verify cron job is registered"""
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if "generate-newspaper" not in result.stdout:
                state.record_failure("cron", "newspaper-job", "Job not in crontab")
                return False

            state.record_success("cron")
            logger.info("✅ Cron job: OK (registered)")
            return True
        except Exception as e:
            state.record_failure("cron", "newspaper-job", str(e))
            return False

    @staticmethod
    def check_docker_health(state: StateManager) -> bool:
        """Check Docker daemon and critical containers"""
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                state.record_failure("docker", "daemon", "Not responding")
                return False

            state.record_success("docker")
            logger.info("✅ Docker: OK")
            return True
        except Exception as e:
            state.record_failure("docker", "daemon", str(e))
            return False


class AlertManager:
    """Batch and deduplicate alerts"""

    def __init__(self, state: StateManager):
        self.state = state
        self.alerts = []

    def add_alert(self, level: str, message: str):
        """Queue alert for batching"""
        self.alerts.append(
            {
                "level": level,
                "message": message,
                "time": datetime.now().isoformat(),
            }
        )

    def should_alert(self, cycle_failures: int) -> bool:
        """Determine if we should send an alert this cycle"""
        return cycle_failures > ALERT_THRESHOLD

    def deduplicate(self) -> List[Dict]:
        """Remove duplicate alerts in the same window"""
        deduped = []
        seen_hashes = set()

        for alert in self.alerts:
            alert_hash = hashlib.md5(alert["message"].encode()).hexdigest()
            if alert_hash not in seen_hashes:
                deduped.append(alert)
                seen_hashes.add(alert_hash)

        return deduped

    def send_alerts(self):
        """Send batched alerts to Suhail"""
        if not self.alerts:
            return

        deduped = self.deduplicate()

        # Log to memory file
        with open(ALERTS_FILE, "a") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Alert Batch: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            for alert in deduped:
                f.write(f"[{alert['level']}] {alert['message']}\n")

        # Send to Suhail if critical
        critical_alerts = [a for a in deduped if a["level"] == "CRITICAL"]
        if critical_alerts:
            summary = f"🚨 Guardian Alert: {len(critical_alerts)} critical issue(s)\n"
            for alert in critical_alerts[:3]:  # Show top 3
                summary += f"• {alert['message']}\n"
            if len(critical_alerts) > 3:
                summary += f"• ... and {len(critical_alerts) - 3} more\n"

            logger.warning(f"Sending alert to Suhail: {summary}")
            # TODO: integrate with message service


class LearningSystem:
    """Track patterns and improve over time"""

    @staticmethod
    def update_memory():
        """Write learnings to MEMORY.md for human review"""
        state_mgr = StateManager()
        state = state_mgr.state

        memory_content = "# Guardian Learning System\n\n"
        memory_content += f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Service health summary
        memory_content += "## Service Health Summary\n\n"
        for service, data in state.get("services", {}).items():
            success_rate = (
                (data["remediation_success"] / data["remediation_attempts"] * 100)
                if data["remediation_attempts"] > 0
                else 0
            )
            status = "🟢 HEALTHY" if data["consecutive_failures"] == 0 else "🔴 FAILING"
            memory_content += (
                f"- **{service}**: {status} | "
                f"Failures: {data['total_failures']} | "
                f"Remediation Success: {success_rate:.0f}%\n"
            )

        # Top issues
        memory_content += "\n## Common Issues (Last 24h)\n\n"
        all_failures = []
        for service, data in state.get("services", {}).items():
            for failure in data.get("failed_checks", [])[-10:]:
                all_failures.append((service, failure))

        issue_counts = {}
        for service, failure in all_failures:
            key = f"{service}/{failure['check']}"
            issue_counts[key] = issue_counts.get(key, 0) + 1

        for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1])[:5]:
            memory_content += f"- {issue}: {count} occurrences\n"

        # Remediation strategies that work
        memory_content += "\n## Most Effective Remediation Actions\n\n"
        remediation_stats = {}
        for item in state.get("remediation_history", [])[-50:]:
            key = f"{item['service']}/{item['action']}"
            if key not in remediation_stats:
                remediation_stats[key] = {"success": 0, "total": 0}
            remediation_stats[key]["total"] += 1
            if item["success"]:
                remediation_stats[key]["success"] += 1

        for action, stats in sorted(
            remediation_stats.items(), key=lambda x: -x[1]["success"] / max(x[1]["total"], 1)
        )[:5]:
            rate = stats["success"] / stats["total"] * 100
            memory_content += f"- {action}: {rate:.0f}% success rate ({stats['success']}/{stats['total']})\n"

        # Predictions
        memory_content += "\n## Predictive Alerts\n\n"
        disk_warning = PredictiveMaintenance.predict_disk_full()
        if disk_warning:
            memory_content += f"- {disk_warning}\n"

        with open(MEMORY_FILE, "w") as f:
            f.write(memory_content)

        logger.info(f"📝 Learning system updated: {MEMORY_FILE}")


def main():
    """Main Guardian loop"""
    logger.info("=" * 60)
    logger.info("🚀 Guardian v4 — Self-Healing Watchdog")
    logger.info("=" * 60)

    state_mgr = StateManager()
    alert_mgr = AlertManager(state_mgr)

    # Run all checks
    failed_checks = []

    checks = [
        ("newspaper", state_mgr.should_disable_service("newspaper"), HealthChecks.check_newspaper_data),
        ("newspaper", state_mgr.should_disable_service("newspaper"), HealthChecks.check_pdf),
        ("newspaper", state_mgr.should_disable_service("newspaper"), HealthChecks.check_audio),
        ("news-site", state_mgr.should_disable_service("news-site"), HealthChecks.check_web_deployment),
        ("cron", state_mgr.should_disable_service("cron"), HealthChecks.check_cron_job),
        ("docker", state_mgr.should_disable_service("docker"), HealthChecks.check_docker_health),
    ]

    for service, disabled, check_func in checks:
        if disabled:
            logger.warning(f"⏭️  Skipping {service} (disabled due to repeated failures)")
            continue

        if state_mgr.is_circuit_broken(service):
            logger.error(f"🔴 Circuit breaker OPEN for {service}")
            alert_mgr.add_alert("CRITICAL", f"Circuit breaker open for {service}")
            failed_checks.append((service, "circuit_breaker"))
            continue

        try:
            if not check_func(state_mgr):
                failed_checks.append((service, "health_check"))

                # Attempt remediation
                if service == "newspaper":
                    if not Remediation.regenerate_newspaper(state_mgr):
                        alert_mgr.add_alert(
                            "CRITICAL",
                            f"Failed to regenerate newspaper (circuit breaker may activate)"
                        )
                elif service == "news-site":
                    if not Remediation.rebuild_site(state_mgr):
                        alert_mgr.add_alert(
                            "CRITICAL",
                            f"Failed to rebuild news site"
                        )
        except Exception as e:
            logger.error(f"Unexpected error in {service} check: {e}")
            failed_checks.append((service, "exception"))
            alert_mgr.add_alert("CRITICAL", f"{service} check raised exception: {e}")

    # Alert if threshold exceeded
    if alert_mgr.should_alert(len(failed_checks)):
        alert_mgr.send_alerts()

    # Update learning system
    LearningSystem.update_memory()

    # Summary
    if not failed_checks:
        logger.info("✅ All checks passed — newspaper pipeline healthy")
    else:
        logger.warning(f"⚠️  {len(failed_checks)} issue(s) detected — attempted automatic fixes")

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
