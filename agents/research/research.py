#!/usr/bin/env python3
"""
Research Agent - Autonomous research query handler.

Performs structured research on topics using web search and content analysis.
Returns JSON with key findings, source credibility, and contradictions.

Usage:
    python3 research.py --topic "AI safety" --keywords "alignment, AGI" --depth 3
    python3 research.py --topic "Climate change" --keywords "carbon, emissions" --depth 2 --output results.json
"""

import argparse
import json
import sys
import logging
from typing import Optional
from datetime import datetime
from pathlib import Path

# Try to import from local functions first, fall back to API calls
try:
    from research_functions import (
        perform_research,
        analyze_sources,
        score_source_credibility,
        detect_contradictions,
        format_output
    )
except ImportError:
    # Define inline implementations if module not found
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the research agent."""
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Autonomous Research Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 research.py --topic "AI safety" --keywords "alignment, AGI" --depth 3
  python3 research.py --topic "Quantum computing" --depth 2 --output results.json
  python3 research.py --topic "Cryptocurrency trends" --keywords "blockchain, DeFi" --depth 3 --format pretty
        """
    )
    
    parser.add_argument(
        '--topic',
        required=True,
        help='Research topic/question'
    )
    parser.add_argument(
        '--keywords',
        default='',
        help='Comma-separated keywords to focus search'
    )
    parser.add_argument(
        '--depth',
        type=int,
        default=2,
        choices=[1, 2, 3],
        help='Research depth: 1=brief (3-5 sources), 2=standard (5-8), 3=deep (8-10)'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output file path (JSON). If not specified, prints to stdout'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'pretty'],
        default='json',
        help='Output format'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Starting research on: {args.topic}")
    if args.keywords:
        logger.info(f"Keywords: {args.keywords}")
    logger.info(f"Depth level: {args.depth}")
    
    # Perform research
    try:
        result = perform_research(
            topic=args.topic,
            keywords=args.keywords,
            depth=args.depth,
            verbose=args.verbose
        )
        
        # Format output
        if args.format == 'pretty':
            output = format_output(result, pretty=True)
        else:
            output = format_output(result, pretty=False)
        
        # Handle output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output)
            logger.info(f"Results saved to: {args.output}")
        else:
            print(output)
        
        return 0
    
    except Exception as e:
        logger.error(f"Research failed: {str(e)}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
