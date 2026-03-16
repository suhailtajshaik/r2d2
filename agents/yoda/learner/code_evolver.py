"""
Code evolver that reads accumulated knowledge and the current source tree,
asks Claude to propose concrete improvements, and applies them.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

import anthropic

from learner.evolution_tracker import EvolutionTracker


_ANALYSIS_SYSTEM_PROMPT = """\
You are a senior ML engineer reviewing a VL-JEPA (Vision-Language Joint-Embedding
Predictive Architecture) codebase alongside a knowledge base of insights extracted
from recent research.

Your task is to propose **specific, actionable improvements** to the code.  For
each proposal include:
1. The file to change (relative path).
2. A short title.
3. A description of what to change and why.
4. The expected benefit (performance, readability, correctness, etc.).

Return your answer as a JSON list of objects:
[
  {
    "file": "src/models/predictor.py",
    "title": "Use FlashAttention in predictor",
    "description": "Replace nn.MultiheadAttention with flash_attn ...",
    "benefit": "2-3x faster training on A100s"
  }
]
Return ONLY valid JSON (no markdown fences).
"""

_EVOLUTION_SYSTEM_PROMPT = """\
You are a senior ML engineer. You will receive:
1. A knowledge base of JEPA research insights.
2. The current source code of a VL-JEPA project.

Produce a list of **concrete code edits** as a JSON list.  Each edit object has:
- "file": relative path of the file to edit (must already exist)
- "title": short summary of the change
- "original": the exact code snippet to replace (must match the file verbatim)
- "replacement": the new code that should replace it
- "reason": why this change improves the codebase

If no changes are warranted, return an empty list: []
Return ONLY valid JSON (no markdown fences).
"""


class CodeEvolver:
    """Evolve the VL-JEPA codebase by applying knowledge-driven improvements.

    The evolver reads the knowledge Markdown files and the current source
    code, asks Claude to propose improvements, and optionally applies them.

    Parameters
    ----------
    knowledge_dir:
        Path to the directory containing knowledge ``.md`` files.
    src_dir:
        Path to the project source directory.
    api_key:
        Anthropic API key.  Falls back to ``ANTHROPIC_API_KEY`` env var.
    """

    MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        knowledge_dir: str = "knowledge",
        src_dir: str = "src",
        api_key: Optional[str] = None,
    ) -> None:
        self.knowledge_dir = knowledge_dir
        self.src_dir = src_dir

        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise ValueError(
                "An Anthropic API key must be provided either as an argument "
                "or via the ANTHROPIC_API_KEY environment variable."
            )
        self._client = anthropic.Anthropic(api_key=resolved_key)
        self._tracker = EvolutionTracker(
            log_path=os.path.join(self.knowledge_dir, "evolution_log.md")
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def analyze(self) -> List[Dict[str, str]]:
        """Propose improvements without applying them.

        Returns
        -------
        list of dict
            Each dict has keys ``file``, ``title``, ``description``, and
            ``benefit``.
        """
        knowledge = self._read_knowledge()
        code = self._read_current_code()

        user_message = (
            "=== KNOWLEDGE BASE ===\n"
            f"{knowledge}\n\n"
            "=== CURRENT CODE ===\n"
            f"{code}"
        )

        try:
            response = self._client.messages.create(
                model=self.MODEL,
                max_tokens=4096,
                system=_ANALYSIS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
        except anthropic.APIError as exc:
            return [{"file": "", "title": "API Error", "description": str(exc), "benefit": ""}]

        return self._parse_json_response(response)

    def evolve(self) -> List[str]:
        """Read knowledge + code, ask Claude for diffs, apply them, and log.

        Returns
        -------
        list of str
            Human-readable descriptions of the changes that were applied.
        """
        knowledge = self._read_knowledge()
        code = self._read_current_code()

        user_message = (
            "=== KNOWLEDGE BASE ===\n"
            f"{knowledge}\n\n"
            "=== CURRENT CODE ===\n"
            f"{code}"
        )

        try:
            response = self._client.messages.create(
                model=self.MODEL,
                max_tokens=8192,
                system=_EVOLUTION_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
        except anthropic.APIError as exc:
            return [f"[ERROR] Claude API call failed: {exc}"]

        edits = self._parse_json_response(response)
        if not edits:
            return ["No changes proposed."]

        applied: List[str] = []
        for edit in edits:
            file_path = os.path.join(self.src_dir, edit.get("file", ""))
            original = edit.get("original", "")
            replacement = edit.get("replacement", "")
            title = edit.get("title", "untitled change")

            if not os.path.isfile(file_path):
                applied.append(f"[SKIP] {title} -- file not found: {file_path}")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as fh:
                    source = fh.read()
            except OSError as exc:
                applied.append(f"[SKIP] {title} -- could not read file: {exc}")
                continue

            if original and original in source:
                new_source = source.replace(original, replacement, 1)
                with open(file_path, "w", encoding="utf-8") as fh:
                    fh.write(new_source)
                applied.append(f"[APPLIED] {title} in {file_path}")
            else:
                applied.append(
                    f"[SKIP] {title} -- original snippet not found in {file_path}"
                )

        # Log the evolution event.
        current_version = self._get_current_version()
        new_version = self._increment_version(current_version)
        self._tracker.log_event(
            version=new_version,
            trigger="code_evolver.evolve()",
            changes=applied,
            reason="Knowledge-driven code evolution",
        )

        return applied

    # ------------------------------------------------------------------ #
    # Knowledge / code readers
    # ------------------------------------------------------------------ #
    def _read_knowledge(self) -> str:
        """Concatenate all Markdown files in the knowledge directory.

        Returns
        -------
        str
            The combined contents, separated by horizontal rules.
        """
        if not os.path.isdir(self.knowledge_dir):
            return "(no knowledge directory found)"

        parts: List[str] = []
        for name in sorted(os.listdir(self.knowledge_dir)):
            if not name.endswith(".md"):
                continue
            path = os.path.join(self.knowledge_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    parts.append(f"--- {name} ---\n{fh.read()}")
            except OSError:
                continue
        return "\n\n".join(parts) if parts else "(knowledge directory is empty)"

    def _read_current_code(self) -> str:
        """Read key Python files from the source directory.

        To keep the prompt within reasonable token limits, only ``.py`` files
        are included and each file is capped at 500 lines.

        Returns
        -------
        str
            A concatenation of ``=== <path> ===`` blocks.
        """
        if not os.path.isdir(self.src_dir):
            return "(no src directory found)"

        parts: List[str] = []
        for root, _dirs, files in os.walk(self.src_dir):
            for fname in sorted(files):
                if not fname.endswith(".py"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as fh:
                        lines = fh.readlines()
                except OSError:
                    continue
                content = "".join(lines[:500])
                rel = os.path.relpath(fpath, start=os.path.dirname(self.src_dir))
                parts.append(f"=== {rel} ===\n{content}")
        return "\n\n".join(parts) if parts else "(src directory is empty)"

    # ------------------------------------------------------------------ #
    # Versioning helpers
    # ------------------------------------------------------------------ #
    def _get_current_version(self) -> str:
        """Return the latest version string from the evolution log.

        Falls back to ``\"0.0.0\"`` when the log is missing or unparseable.
        """
        return self._tracker.get_current_version()

    @staticmethod
    def _increment_version(current: str) -> str:
        """Bump the patch segment of a semver-style version string.

        Parameters
        ----------
        current:
            A version string like ``\"1.2.3\"``.

        Returns
        -------
        str
            The incremented version, e.g. ``\"1.2.4\"``.
        """
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", current)
        if not match:
            return "0.0.1"
        major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return f"{major}.{minor}.{patch + 1}"

    # ------------------------------------------------------------------ #
    # Response parsing
    # ------------------------------------------------------------------ #
    @staticmethod
    def _parse_json_response(response: object) -> List[Dict[str, str]]:
        """Extract a JSON list from Claude's response text."""
        import json

        raw = response.content[0].text.strip()

        # Strip optional markdown fences.
        if raw.startswith("```"):
            lines = raw.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            raw = "\n".join(lines)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return [{"file": "", "title": "Parse Error", "description": "Could not parse response as JSON", "benefit": ""}]

        if isinstance(data, list):
            return data
        return [data]
