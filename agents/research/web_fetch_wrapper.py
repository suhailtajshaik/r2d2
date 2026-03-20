"""
Web fetch wrapper for content extraction.

This module wraps the OpenClaw web_fetch tool for use in the research agent.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def fetch_content(url: str, max_chars: int = 5000) -> Optional[str]:
    """
    Fetch and extract readable content from a URL.
    
    This function is designed to be called by the research agent.
    In production, it will invoke the OpenClaw web_fetch tool.
    
    Args:
        url: URL to fetch
        max_chars: Maximum characters to return
    
    Returns:
        Extracted content as string, or None if fetch failed
    """
    
    logger.debug(f"Fetching content from: {url}")
    
    # The actual implementation would call the web_fetch tool
    # For standalone execution, this returns a placeholder
    
    # Expected tool format:
    # web_fetch(url=url, extractMode='markdown', maxChars=max_chars)
    
    # Returns extracted markdown/text content
    
    # Placeholder - in actual deployment, this would use:
    # from openclaw.tools import web_fetch
    # return web_fetch(url, extractMode='markdown', maxChars=max_chars)
    
    logger.warning("fetch_content called in standalone mode - implement tool integration")
    return None


def extract_metadata(content: str) -> dict:
    """
    Extract metadata from fetched content.
    
    Args:
        content: Fetched content
    
    Returns:
        Metadata dict (title, author, date, etc.)
    """
    
    # Simple metadata extraction
    metadata = {
        'length': len(content),
        'word_count': len(content.split()),
        'has_code': '```' in content or '<code>' in content,
        'has_links': 'http' in content,
    }
    
    return metadata
