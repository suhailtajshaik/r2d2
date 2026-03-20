"""
Core research functions for the Research Agent.

Handles web search, content fetching, analysis, and structured output.
"""

import json
import logging
import re
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class Source:
    """Represents a research source."""
    title: str
    url: str
    domain: str
    content: Optional[str] = None
    credibility_score: float = 0.0
    publication_date: Optional[str] = None
    relevance: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'url': self.url,
            'domain': self.domain,
            'credibility_score': round(self.credibility_score, 2),
            'publication_date': self.publication_date,
            'relevance': round(self.relevance, 2),
            'content_preview': self.content[:200] + '...' if self.content else None
        }


@dataclass
class ResearchResult:
    """Structured research output."""
    topic: str
    keywords: List[str]
    timestamp: str
    depth: int
    key_findings: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    credibility_analysis: Dict[str, Any]
    consensus: str
    contradictions: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


def perform_research(
    topic: str,
    keywords: str = '',
    depth: int = 2,
    verbose: bool = False
) -> ResearchResult:
    """
    Perform structured research on a topic.
    
    Args:
        topic: Research topic/question
        keywords: Comma-separated keywords
        depth: Research depth (1-3)
        verbose: Enable verbose logging
    
    Returns:
        ResearchResult with findings and analysis
    """
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Initiating research on: {topic}")
    
    # Parse keywords
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
    
    # Determine search parameters based on depth
    num_results = {1: 5, 2: 8, 3: 10}.get(depth, 8)
    num_fetch = {1: 3, 2: 5, 3: 8}.get(depth, 5)
    
    logger.debug(f"Searching for {num_results} results, fetching top {num_fetch}")
    
    # Step 1: Web search
    logger.info("Step 1: Performing web search...")
    search_results = search_web(topic, keyword_list, num_results)
    logger.info(f"Found {len(search_results)} results")
    
    if not search_results:
        raise ValueError(f"No search results found for: {topic}")
    
    # Step 2: Fetch full content from top sources
    logger.info(f"Step 2: Fetching content from top {num_fetch} sources...")
    sources = fetch_source_content(search_results[:num_fetch])
    logger.info(f"Successfully fetched {len(sources)} sources")
    
    # Step 3: Analyze sources
    logger.info("Step 3: Analyzing sources...")
    for source in sources:
        source.credibility_score = score_source_credibility(source)
        source.relevance = calculate_relevance(source, keyword_list)
    
    # Sort by credibility and relevance
    sources.sort(
        key=lambda s: (s.credibility_score * 0.6 + s.relevance * 0.4),
        reverse=True
    )
    
    # Step 4: Extract key findings
    logger.info("Step 4: Extracting key findings...")
    key_findings = extract_key_findings(sources, keyword_list)
    
    # Step 5: Detect consensus and contradictions
    logger.info("Step 5: Analyzing consensus and contradictions...")
    consensus = analyze_consensus(sources, key_findings)
    contradictions = detect_contradictions(sources, key_findings)
    
    # Step 6: Create credibility analysis
    credibility_analysis = analyze_credibility_distribution(sources)
    
    # Create result
    result = ResearchResult(
        topic=topic,
        keywords=keyword_list,
        timestamp=datetime.utcnow().isoformat() + 'Z',
        depth=depth,
        key_findings=key_findings,
        sources=[s.to_dict() for s in sources],
        credibility_analysis=credibility_analysis,
        consensus=consensus,
        contradictions=contradictions,
        metadata={
            'total_sources_found': len(search_results),
            'sources_analyzed': len(sources),
            'research_duration_note': 'See timestamp for research time'
        }
    )
    
    logger.info("Research complete!")
    return result


def search_web(
    topic: str,
    keywords: List[str],
    num_results: int = 8
) -> List[Dict[str, Any]]:
    """
    Perform web search using Perplexity API.
    
    Args:
        topic: Research topic
        keywords: List of keywords
        num_results: Number of results to return
    
    Returns:
        List of search results
    """
    
    # Build search query
    search_query = topic
    if keywords:
        search_query += ' ' + ' '.join(keywords)
    
    logger.debug(f"Search query: {search_query}")
    
    # This would normally call the Perplexity web_search tool
    # For now, return a structured format that expects tool integration
    
    try:
        # Import here to avoid circular imports
        from web_search_wrapper import search_perplexity
        return search_perplexity(search_query, num_results)
    except ImportError:
        logger.warning("web_search_wrapper not available, using mock search")
        return []


def fetch_source_content(
    search_results: List[Dict[str, Any]]
) -> List[Source]:
    """
    Fetch full content from search results.
    
    Args:
        search_results: List of search result dicts
    
    Returns:
        List of Source objects with full content
    """
    
    sources = []
    
    for result in search_results:
        try:
            # Import here to avoid circular imports
            from web_fetch_wrapper import fetch_content
            
            url = result.get('url')
            if not url:
                continue
            
            content = fetch_content(url)
            
            source = Source(
                title=result.get('title', 'Unknown'),
                url=url,
                domain=extract_domain(url),
                content=content,
                publication_date=extract_date(result.get('snippet', ''))
            )
            sources.append(source)
            logger.debug(f"Fetched: {source.domain}")
        
        except Exception as e:
            logger.debug(f"Failed to fetch {result.get('url')}: {str(e)}")
    
    return sources


def score_source_credibility(source: Source) -> float:
    """
    Score source credibility based on domain and content.
    
    Args:
        source: Source object
    
    Returns:
        Credibility score (0.0-1.0)
    """
    
    score = 0.5  # Base score
    
    # Domain reputation
    trusted_domains = {
        'nature.com': 0.95,
        'science.org': 0.95,
        'arxiv.org': 0.90,
        'ieee.org': 0.90,
        'acm.org': 0.90,
        'nytimes.com': 0.85,
        'bbc.com': 0.85,
        'economist.com': 0.85,
        'github.com': 0.85,
        'wikipedia.org': 0.75,
        'medium.com': 0.65,
        'linkedin.com': 0.65,
        'twitter.com': 0.60,
        'youtube.com': 0.60,
        'reddit.com': 0.55,
    }
    
    domain = source.domain.lower()
    for trusted_domain, trusted_score in trusted_domains.items():
        if trusted_domain in domain:
            score = trusted_score
            break
    
    # Content quality boost
    if source.content:
        content_length = len(source.content)
        if content_length > 1000:
            score = min(score + 0.1, 1.0)
        
        # Check for citations/references
        if 'reference' in source.content.lower() or 'citation' in source.content.lower():
            score = min(score + 0.05, 1.0)
    
    return score


def calculate_relevance(source: Source, keywords: List[str]) -> float:
    """
    Calculate source relevance to keywords.
    
    Args:
        source: Source object
        keywords: List of keywords
    
    Returns:
        Relevance score (0.0-1.0)
    """
    
    if not keywords or not source.content:
        return 0.5
    
    content = (source.title + ' ' + source.content).lower()
    matches = sum(1 for kw in keywords if kw.lower() in content)
    
    return min(matches / max(len(keywords), 1) * 0.8 + 0.2, 1.0)


def extract_key_findings(
    sources: List[Source],
    keywords: List[str]
) -> List[Dict[str, Any]]:
    """
    Extract key findings from sources.
    
    Args:
        sources: List of sources
        keywords: List of keywords for filtering
    
    Returns:
        List of key findings
    """
    
    findings = []
    seen = set()
    
    for source in sources[:5]:  # Top 5 sources
        if not source.content:
            continue
        
        # Extract sentences containing keywords
        content = source.content
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 20:
                continue
            
            # Check if sentence is relevant
            is_relevant = any(kw.lower() in sentence.lower() for kw in keywords) if keywords else True
            
            if is_relevant and sentence not in seen:
                findings.append({
                    'statement': sentence[:200],
                    'source_url': source.url,
                    'confidence': 'high' if source.credibility_score > 0.8 else 'medium'
                })
                seen.add(sentence)
                
                if len(findings) >= 5:
                    return findings
    
    return findings


def analyze_consensus(
    sources: List[Source],
    key_findings: List[Dict[str, Any]]
) -> str:
    """
    Analyze consensus across sources.
    
    Args:
        sources: List of sources
        key_findings: Key findings
    
    Returns:
        Consensus analysis string
    """
    
    if not key_findings:
        return "Insufficient data to determine consensus"
    
    high_credibility_count = sum(1 for s in sources if s.credibility_score > 0.8)
    total_sources = len(sources)
    
    if high_credibility_count == 0:
        return "Mixed credibility sources; consensus unclear"
    
    consensus_ratio = high_credibility_count / total_sources
    
    if consensus_ratio > 0.8:
        return "Strong consensus across high-credibility sources"
    elif consensus_ratio > 0.6:
        return "Moderate consensus across sources"
    else:
        return "Weak consensus; sources present varied perspectives"


def detect_contradictions(
    sources: List[Source],
    key_findings: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Detect contradictions in the research.
    
    Args:
        sources: List of sources
        key_findings: Key findings
    
    Returns:
        List of contradictions
    """
    
    contradictions = []
    
    # Look for opposite sentiments or claims
    negative_words = {'not', 'no', 'false', 'wrong', 'incorrect', 'unlikely'}
    positive_words = {'yes', 'true', 'correct', 'likely', 'confirmed'}
    
    for i, finding1 in enumerate(key_findings):
        for finding2 in key_findings[i+1:]:
            stmt1 = finding1['statement'].lower()
            stmt2 = finding2['statement'].lower()
            
            # Simple contradiction detection
            has_neg1 = any(word in stmt1 for word in negative_words)
            has_neg2 = any(word in stmt2 for word in negative_words)
            has_pos1 = any(word in stmt1 for word in positive_words)
            has_pos2 = any(word in stmt2 for word in positive_words)
            
            if (has_neg1 and has_pos2) or (has_pos1 and has_neg2):
                # Check if they're about similar topics
                common_words = set(stmt1.split()) & set(stmt2.split())
                if len(common_words) > 3:
                    contradictions.append({
                        'claim_1': finding1['statement'][:100],
                        'source_1': finding1['source_url'],
                        'claim_2': finding2['statement'][:100],
                        'source_2': finding2['source_url'],
                        'severity': 'high' if len(common_words) > 5 else 'medium'
                    })
    
    return contradictions[:3]  # Return top 3 contradictions


def analyze_credibility_distribution(sources: List[Source]) -> Dict[str, Any]:
    """
    Analyze credibility score distribution.
    
    Args:
        sources: List of sources
    
    Returns:
        Credibility analysis
    """
    
    if not sources:
        return {}
    
    scores = [s.credibility_score for s in sources]
    
    return {
        'average_score': round(sum(scores) / len(scores), 2),
        'highest_score': round(max(scores), 2),
        'lowest_score': round(min(scores), 2),
        'high_credibility_count': sum(1 for s in scores if s > 0.8),
        'medium_credibility_count': sum(1 for s in scores if 0.6 <= s <= 0.8),
        'low_credibility_count': sum(1 for s in scores if s < 0.6),
    }


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc or url
    except:
        return url


def extract_date(text: str) -> Optional[str]:
    """Extract date from text."""
    # Simple date extraction (YYYY-MM-DD)
    match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    return match.group(0) if match else None


def format_output(result: ResearchResult, pretty: bool = False) -> str:
    """
    Format research result for output.
    
    Args:
        result: ResearchResult object
        pretty: Whether to pretty-print JSON
    
    Returns:
        Formatted JSON string
    """
    
    result_dict = result.to_dict()
    
    if pretty:
        return json.dumps(result_dict, indent=2)
    else:
        return json.dumps(result_dict)
