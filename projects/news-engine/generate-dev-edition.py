#!/usr/bin/env python3
"""
Generate Headlines Today edition using news-engine for DEV deployment.
Outputs to dev archive: /home/r2d2/projects/news-site/public/archive-dev/YYYY/MM/DD/

FAST MODE (current):
- Fetches RSS feeds
- Applies fact-checking (built-in, no web search)
- Extracts intent
- Generates PDF + audio
- ~60 seconds total

TODO: Full mode with web_search
- Enable research layer (requires OpenClaw subagent context)
- This is the main purpose of news-engine: FACT-CHECKING with verification
- When deployed as OpenClaw subagent: Add web_search-based research
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from newspaper_runner_fast import FastNewspaperRunner

def main():
    print("=" * 70)
    print("📰 NEWS ENGINE - DEV EDITION BUILDER")
    print("Generating for: https://lab.suhailtaj.cloud/the-headlines-today-dev/")
    print("=" * 70)
    print()
    
    try:
        # Use separate dev output directory
        dev_output_dir = '/home/r2d2/projects/news-site/public/archive-dev'
        
        # Initialize fast runner (skips research layer)
        runner = FastNewspaperRunner(
            config_path='config.yaml',
            output_dir=dev_output_dir,
            verbose=True
        )
        
        # Run fast edition
        result = runner.run_edition()
        
        # Print results
        print()
        print("-" * 70)
        if result['success']:
            print(f"✅ SUCCESS")
            print(f"   Date: {result['date']}")
            print(f"   Articles: {result['articles']}")
            print(f"   JSON: {result['json_path']}")
            print(f"   PDF: {result['pdf_path']}")
            if result.get('audio_path'):
                print(f"   Audio: {result['audio_path']}")
            print()
            print("🌐 Live at: https://news-dev.suhailtaj.cloud/archive/...")
            print("-" * 70)
            return 0
        else:
            print(f"❌ FAILED")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print("-" * 70)
            return 1
    
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
