"""
Evolution tracker that maintains a timestamped Markdown log of every
code-evolution event.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional


class EvolutionTracker:
    """Append-only log of code-evolution events.

    Each event records a version string, the trigger that caused it, a list
    of changes, and a human-readable reason.  Events are persisted as
    Markdown sections in a single log file.

    Parameters
    ----------
    log_path:
        Path to the evolution log Markdown file.  Created on first write.
    """

    # Regex for parsing version headers written by :meth:`log_event`.
    _VERSION_RE = re.compile(
        r"^##\s+Version\s+(\d+\.\d+\.\d+)\s+\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\]"
    )

    def __init__(self, log_path: str = "knowledge/evolution_log.md") -> None:
        self.log_path = log_path

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def log_event(
        self,
        version: str,
        trigger: str,
        changes: List[str],
        reason: str,
    ) -> None:
        """Append a new evolution event to the log.

        Parameters
        ----------
        version:
            Semver-style version string for this evolution step.
        trigger:
            What initiated the evolution (e.g. ``"code_evolver.evolve()"``).
        changes:
            List of human-readable descriptions of individual changes.
        reason:
            High-level reason / motivation for the evolution.
        """
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)

        # Create the file with a title if it does not exist yet.
        if not os.path.isfile(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as fh:
                fh.write("# Evolution Log\n\n")

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        lines = [
            f"## Version {version} [{timestamp}]",
            f"**Trigger:** {trigger}",
            f"**Reason:** {reason}",
            "",
            "### Changes",
        ]
        for change in changes:
            lines.append(f"- {change}")
        lines.append("")  # trailing newline
        block = "\n".join(lines) + "\n"

        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(block)

    def get_current_version(self) -> str:
        """Parse the log and return the latest version string.

        Returns
        -------
        str
            The most recent version found, or ``"0.0.0"`` if the log is
            empty or does not exist.
        """
        if not os.path.isfile(self.log_path):
            return "0.0.0"

        latest: Optional[str] = None
        try:
            with open(self.log_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    m = self._VERSION_RE.match(line)
                    if m:
                        latest = m.group(1)
        except OSError:
            return "0.0.0"

        return latest if latest is not None else "0.0.0"

    def get_history(self) -> List[Dict[str, object]]:
        """Return the full evolution history as a list of dicts.

        Each dict contains:

        - ``version`` (str)
        - ``timestamp`` (str, ``"YYYY-MM-DD HH:MM"``)
        - ``trigger`` (str)
        - ``changes`` (list of str)

        Returns
        -------
        list of dict
            Ordered from oldest to newest.
        """
        if not os.path.isfile(self.log_path):
            return []

        try:
            with open(self.log_path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except OSError:
            return []

        entries: List[Dict[str, object]] = []
        current: Optional[Dict[str, object]] = None

        for line in content.splitlines():
            version_match = self._VERSION_RE.match(line)
            if version_match:
                # Save the previous entry before starting a new one.
                if current is not None:
                    entries.append(current)
                current = {
                    "version": version_match.group(1),
                    "timestamp": version_match.group(2),
                    "trigger": "",
                    "changes": [],
                }
                continue

            if current is None:
                continue

            # Parse trigger line.
            if line.startswith("**Trigger:**"):
                current["trigger"] = line.replace("**Trigger:**", "").strip()
                continue

            # Collect change bullet points.
            if line.startswith("- "):
                current["changes"].append(line[2:])  # type: ignore[union-attr]

        # Don't forget the last entry.
        if current is not None:
            entries.append(current)

        return entries
