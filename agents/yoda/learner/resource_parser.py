"""
Resource parser for ingesting research papers, web articles, and raw text
into a standardised document dict consumed by the knowledge extractor.
"""

from __future__ import annotations

import os
from typing import Dict

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # type: ignore[assignment]

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None  # type: ignore[assignment]
    BeautifulSoup = None  # type: ignore[assignment,misc]


class ResourceParser:
    """Parse PDFs, URLs, and raw text into a uniform document representation.

    Every ``parse_*`` method returns a dict with the keys *source*, *content*,
    and *type* so that downstream components can handle all resource types
    identically.
    """

    # ------------------------------------------------------------------ #
    # PDF
    # ------------------------------------------------------------------ #
    def parse_pdf(self, file_path: str) -> Dict[str, str]:
        """Extract clean text from every page of a PDF file.

        Parameters
        ----------
        file_path:
            Absolute or relative path to a ``.pdf`` file.

        Returns
        -------
        dict
            ``{"source": <path>, "content": <text>, "type": "pdf"}``

        Raises
        ------
        FileNotFoundError
            If *file_path* does not point to an existing file.
        RuntimeError
            If PyMuPDF cannot open or read the file.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if fitz is None:
            raise ImportError("PyMuPDF (fitz) is required for PDF parsing. Install with: pip install PyMuPDF")

        try:
            doc = fitz.open(file_path)
        except Exception as exc:
            raise RuntimeError(f"Failed to open PDF {file_path}: {exc}") from exc

        pages: list[str] = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages.append(text.strip())
        doc.close()

        content = "\n\n".join(pages)
        return {"source": file_path, "content": content, "type": "pdf"}

    # ------------------------------------------------------------------ #
    # URL
    # ------------------------------------------------------------------ #
    def parse_url(self, url: str) -> Dict[str, str]:
        """Fetch a web page and extract its main textual content.

        Scripts, styles, navigation elements, headers, and footers are
        stripped.  The parser prefers ``<article>`` or ``<main>`` tags when
        present; otherwise it falls back to the full ``<body>``.

        Parameters
        ----------
        url:
            An ``http`` or ``https`` URL.

        Returns
        -------
        dict
            ``{"source": <url>, "content": <text>, "type": "url"}``

        Raises
        ------
        requests.RequestException
            On any network-level failure.
        """
        if requests is None:
            raise ImportError("requests and beautifulsoup4 are required for URL parsing. Install with: pip install requests beautifulsoup4")

        response = requests.get(url, timeout=30, headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; VL-JEPA-Learner/1.0; "
                "+https://github.com/yoda)"
            ),
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove elements that contribute noise rather than content.
        for tag in soup.find_all(
            ["script", "style", "nav", "header", "footer", "aside", "form"]
        ):
            tag.decompose()

        # Prefer semantic containers.
        main = soup.find("article") or soup.find("main") or soup.find("body")
        if main is None:
            content = soup.get_text(separator="\n", strip=True)
        else:
            content = main.get_text(separator="\n", strip=True)

        # Collapse excessive blank lines.
        lines = [line.strip() for line in content.splitlines()]
        content = "\n".join(line for line in lines if line)

        return {"source": url, "content": content, "type": "url"}

    # ------------------------------------------------------------------ #
    # Raw text
    # ------------------------------------------------------------------ #
    def parse_text(self, text: str, source: str = "direct_input") -> Dict[str, str]:
        """Wrap raw text in the standard document dict.

        Parameters
        ----------
        text:
            The raw text content.
        source:
            An optional label describing where the text came from.

        Returns
        -------
        dict
            ``{"source": <source>, "content": <text>, "type": "text"}``
        """
        return {"source": source, "content": text, "type": "text"}

    # ------------------------------------------------------------------ #
    # Auto-detect
    # ------------------------------------------------------------------ #
    def parse(self, source: str) -> Dict[str, str]:
        """Auto-detect the source type and delegate to the right parser.

        Detection rules (applied in order):

        1. If *source* ends with ``.pdf`` **and** the file exists on disk,
           treat it as a PDF.
        2. If *source* starts with ``http://`` or ``https://``, treat it as
           a URL.
        3. Otherwise treat it as raw text.

        Parameters
        ----------
        source:
            A file path, URL, or raw text string.

        Returns
        -------
        dict
            The standard document dict produced by the matched parser.
        """
        if source.lower().endswith(".pdf"):
            return self.parse_pdf(source)
        if source.startswith("http://") or source.startswith("https://"):
            return self.parse_url(source)
        return self.parse_text(source)
