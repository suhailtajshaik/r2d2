"""
Knowledge updater that appends extracted insights to per-category Markdown
files inside the knowledge directory.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Dict, List


# Map extraction dict keys to their target Markdown files.
_CATEGORY_FILES: Dict[str, str] = {
    "concepts": "concepts.md",
    "architecture": "architecture.md",
    "training": "training_insights.md",
    "datasets": "datasets.md",
    "code_improvements": "code_improvements.md",
}


class KnowledgeUpdater:
    """Persist extracted insights by appending them to Markdown files.

    Each category (concepts, architecture, training, datasets,
    code_improvements) maps to a dedicated ``.md`` file.  New entries are
    always *appended* -- existing content is never overwritten.

    Parameters
    ----------
    knowledge_dir:
        Directory where knowledge Markdown files are stored.  Created
        automatically if it does not exist.
    """

    def __init__(self, knowledge_dir: str = "knowledge") -> None:
        self.knowledge_dir = knowledge_dir
        os.makedirs(self.knowledge_dir, exist_ok=True)

    def update(self, extracted: Dict[str, List[str]], source: str) -> List[str]:
        """Append *extracted* insights to the appropriate Markdown files.

        Parameters
        ----------
        extracted:
            A dict produced by :class:`KnowledgeExtractor` with keys
            ``concepts``, ``architecture``, ``training``, ``datasets``, and
            ``code_improvements``.
        source:
            Human-readable origin label (file path, URL, etc.).

        Returns
        -------
        list of str
            Absolute paths to the files that were updated (i.e. that received
            at least one new bullet point).
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        updated_files: List[str] = []

        for category, filename in _CATEGORY_FILES.items():
            items = extracted.get(category, [])
            if not items:
                continue

            # Skip entries that are purely error markers.
            if all(item.startswith("[ERROR]") or item.startswith("[PARSE ERROR]") for item in items):
                continue

            file_path = os.path.join(self.knowledge_dir, filename)
            self._ensure_file_header(file_path, category)

            block = self._format_block(timestamp, source, items)
            with open(file_path, "a", encoding="utf-8") as fh:
                fh.write(block)

            updated_files.append(os.path.abspath(file_path))

        return updated_files

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    @staticmethod
    def _format_block(timestamp: str, source: str, items: List[str]) -> str:
        """Build a Markdown block for one category update.

        Format::

            ## [2025-06-01 14:30] Source: <source>
            - First insight
            - Second insight

        """
        lines = [f"## [{timestamp}] Source: {source}"]
        for item in items:
            # Normalise: strip leading bullet/dash if the model already added one.
            clean = item.lstrip("-*").strip()
            if clean:
                lines.append(f"- {clean}")
        lines.append("")  # trailing newline
        return "\n".join(lines) + "\n"

    @staticmethod
    def _ensure_file_header(file_path: str, category: str) -> None:
        """Create the file with a title header if it does not yet exist."""
        if os.path.isfile(file_path):
            return
        title = category.replace("_", " ").title()
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(f"# {title}\n\n")
