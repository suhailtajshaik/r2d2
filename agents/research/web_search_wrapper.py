"""
Web search wrapper for Perplexity API integration.

This module wraps the OpenClaw web_search tool for use in the research agent.
"""

import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def search_perplexity(query: str, num_results: int = 8) -> List[Dict[str, Any]]:
    """
    Perform web search using Perplexity API.
    
    This function is designed to be called by the research agent.
    In production, it will invoke the OpenClaw web_search tool.
    
    Args:
        query: Search query string
        num_results: Number of results to return (max 10)
    
    Returns:
        List of search results with title, url, snippet
    """
    
    logger.info(f"Searching for: {query}")
    
    # The actual implementation would call the web_search tool
    # For standalone execution, this returns a placeholder
    
    # Expected tool format:
    # web_search(query=query, count=min(num_results, 10))
    
    # Returns list of dicts like:
    # {
    #     'title': str,
    #     'url': str,
    #     'snippet': str,
    #     'source': str  (optional)
    # }
    
    # Placeholder - in actual deployment, this would use:
    # from openclaw.tools import web_search
    # return web_search(query, count=num_results)
    
    logger.warning("search_perplexity called in standalone mode - implement tool integration")
    return []


def parse_search_results(raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse raw search results into standardized format.
    
    Args:
        raw_results: Raw results from search API
    
    Returns:
        Standardized results
    """
    
    parsed = []
    
    for result in raw_results:
        parsed.append({
            'title': result.get('title', ''),
            'url': result.get('url', ''),
            'snippet': result.get('snippet', result.get('description', '')),
            'source': result.get('source', 'web')
        })
    
    return parsed
