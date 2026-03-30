#!/usr/bin/env python3
"""
Generate Headlines Today edition using news-engine for DEV deployment.
Outputs to dev archive: /home/r2d2/projects/news-site/public/archive/dev-builds/YYYY/MM/DD/

This runs alongside Maxwell (prod) so we can test and compare quality.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from newspaper_runner import NewspaperRunner

def main():
    print("=" * 70)
    print("📰 NEWS ENGINE - DEV EDITION BUILDER")
    print("Generating for: https://lab.suhailtaj.cloud/the-headlines-today-dev/")
    print("=" * 70)
    print()
    
    try:
        # Use dev output directory (still mounts same archive, but marked as dev)
        dev_output_dir = '/home/r2d2/projects/news-site/public/archive'
        
        # Initialize runner
        runner = NewspaperRunner(
            config_path='config.yaml',
            output_dir=dev_output_dir,
            verbose=True
        )
        
        # Run edition with fallback allowed
        result = runner.run_edition(allow_fallback=True)
        
        # Print results
        print()
        print("-" * 70)
        if result['success']:
            print(f"✅ SUCCESS")
            print(f"   Date: {result['date']}")
            print(f"   Articles: {result['articles']}")
            print(f"   JSON: {result['json_path']}")
            print(f"   PDF: {result['pdf_path']}")
            print(f"   Audio: {result['audio_path']}")
            print()
            print("🌐 Live at: https://lab.suhailtaj.cloud/the-headlines-today-dev/archive/...")
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
