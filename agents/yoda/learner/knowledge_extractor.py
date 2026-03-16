"""
Knowledge extractor that uses Anthropic's Claude API to distil structured
insights from parsed research content.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import anthropic


_SYSTEM_PROMPT = """\
You are a research assistant specialised in deep learning, with particular
expertise in Joint-Embedding Predictive Architecture (JEPA) and its variants
(I-JEPA for images, V-JEPA and VL-JEPA for video/vision-language).

JEPA is a self-supervised learning paradigm proposed by Yann LeCun and
collaborators.  Key characteristics:
- Operates in a learned *representation space*, not pixel space.
- Uses a *context encoder* to encode visible patches and a *predictor* to
  predict the representations of masked (target) patches.
- A *target encoder* (updated via exponential moving average) provides the
  prediction targets.
- Avoids representational collapse without negative pairs or pixel
  reconstruction.
- VL-JEPA extends this to multimodal (vision + language) settings.

Given the content below, extract actionable insights organised into exactly
five categories.  Return **only** valid JSON (no markdown fences) with these
keys, each mapping to a list of concise bullet-point strings:

{
  "concepts": [
    "Core theoretical ideas, design principles, and intuitions."
  ],
  "architecture": [
    "Specific architectural details: layers, attention patterns, masking "
    "strategies, encoder/predictor design, positional embeddings, etc."
  ],
  "training": [
    "Training procedures, hyperparameters, schedules, loss functions, "
    "optimiser settings, regularisation, data augmentation, EMA schedules."
  ],
  "datasets": [
    "Datasets mentioned, data curation strategies, preprocessing, and "
    "benchmarks used for evaluation."
  ],
  "code_improvements": [
    "Concrete suggestions for improving an existing JEPA / VL-JEPA "
    "codebase: better abstractions, performance tips, new features, "
    "bug-avoidance patterns."
  ]
}

Be specific and quantitative where possible (e.g. \"learning rate 1.5e-4
with cosine decay over 300 epochs\").  If a category has no relevant
information, return an empty list for that key.
"""


class KnowledgeExtractor:
    """Extract structured JEPA-relevant knowledge from free-form text via Claude.

    Parameters
    ----------
    api_key:
        Anthropic API key.  Falls back to the ``ANTHROPIC_API_KEY``
        environment variable when *None*.
    """

    MODEL = "claude-3-5-haiku-latest"

    def __init__(self, api_key: Optional[str] = None) -> None:
        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise ValueError(
                "An Anthropic API key must be provided either as an argument "
                "or via the ANTHROPIC_API_KEY environment variable."
            )
        self._client = anthropic.Anthropic(api_key=resolved_key)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def extract(self, content: str, source: str) -> Dict[str, List[str]]:
        """Extract structured knowledge from *content*.

        Parameters
        ----------
        content:
            The full text of the parsed resource (paper, article, etc.).
        source:
            A human-readable label for the resource (file path, URL, ...).

        Returns
        -------
        dict
            A mapping with keys ``concepts``, ``architecture``, ``training``,
            ``datasets``, and ``code_improvements``, each holding a list of
            short insight strings.
        """
        user_message = (
            f"Source: {source}\n\n"
            f"--- BEGIN CONTENT ---\n{content}\n--- END CONTENT ---"
        )

        try:
            response = self._client.messages.create(
                model=self.MODEL,
                max_tokens=4096,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
        except anthropic.APIConnectionError as exc:
            return self._empty_result(
                f"API connection error: {exc}"
            )
        except anthropic.RateLimitError as exc:
            return self._empty_result(
                f"Rate limit exceeded: {exc}"
            )
        except anthropic.APIStatusError as exc:
            return self._empty_result(
                f"API error (status {exc.status_code}): {exc.message}"
            )

        return self._parse_response(response)

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    @staticmethod
    def _empty_result(error_msg: str) -> Dict[str, List[str]]:
        """Return a result dict with a single error entry in every category."""
        return {
            "concepts": [f"[ERROR] {error_msg}"],
            "architecture": [],
            "training": [],
            "datasets": [],
            "code_improvements": [],
        }

    @staticmethod
    def _parse_response(
        response: Any,
    ) -> Dict[str, List[str]]:
        """Parse the Claude response into the expected dict format."""
        import json

        raw_text = response.content[0].text.strip()

        # The model sometimes wraps JSON in markdown code fences.
        if raw_text.startswith("```"):
            # Strip opening fence (with optional language tag) and closing fence.
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            raw_text = "\n".join(lines)

        expected_keys = {
            "concepts",
            "architecture",
            "training",
            "datasets",
            "code_improvements",
        }

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            return {
                "concepts": [f"[PARSE ERROR] Could not parse API response as JSON."],
                "architecture": [],
                "training": [],
                "datasets": [],
                "code_improvements": [],
            }

        # Ensure every expected key is present and holds a list of strings.
        result: Dict[str, List[str]] = {}
        for key in expected_keys:
            value = data.get(key, [])
            if isinstance(value, list):
                result[key] = [str(item) for item in value]
            else:
                result[key] = [str(value)]

        return result
