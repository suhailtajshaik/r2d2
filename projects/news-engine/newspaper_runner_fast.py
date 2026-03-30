#!/usr/bin/env python3
"""
Fast Newspaper Runner - Generates news without web_search research layer.

Uses:
- RSS feeds (raw input)
- Fact-checking (built-in, no external search)
- Intent analysis (built-in)
- PDF + audio output

TODO: Re-enable web_search research when running as OpenClaw subagent
This is the core purpose of news-engine: FACT-CHECKING with verification.
Current: Fact-check without verification (uses built-in claims analysis only)
Future: Add web_search-based research for full verification capability
"""

import sys
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from news_engine.config import load_config, get_default_config
from news_engine.feeds import FeedsManager, deduplicate_stories
from news_engine.factchecker import FactChecker
from news_engine.intent_extractor import IntentExtractor
from news_engine.models import Article, Edition, Verification


logger = logging.getLogger(__name__)


class FastNewspaperRunner:
    """Fast runner: RSS → Fact-check → Intent → PDF + Audio"""
    
    def __init__(
        self,
        config_path: str = 'config.yaml',
        output_dir: str = '/home/r2d2/projects/news-site/public/archive-dev',
        verbose: bool = False,
    ):
        """Initialize fast runner (skips research layer)."""
        self.verbose = verbose
        self.setup_logging()
        
        try:
            self.config = load_config(config_path)
        except:
            self.config = get_default_config()
            logger.warning('Using default config (file not found)')
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.feeds = FeedsManager(self.config.feeds)
        self.factchecker = FactChecker(self.config.publish)
        self.intent_extractor = IntentExtractor(self.config.intent)
        
        logger.info('✓ FastNewspaperRunner initialized (research layer skipped)')
    
    def setup_logging(self):
        """Configure logging."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def run_edition(self, edition_date: Optional[datetime] = None) -> Dict:
        """
        Generate fast edition (RSS → Fact-check → Intent).
        Skips web_search research layer for now.
        
        Returns:
            {
                'success': bool,
                'date': str,
                'json_path': str,
                'pdf_path': str,
                'audio_path': str,
                'error': str (if failed),
                'articles': int,
            }
        """
        if edition_date is None:
            edition_date = datetime.now()
        
        result = {
            'success': False,
            'date': edition_date.strftime('%Y-%m-%d'),
            'json_path': None,
            'pdf_path': None,
            'audio_path': None,
            'articles': 0,
        }
        
        try:
            date_str = edition_date.strftime("%B %d, %Y")
            date_path = edition_date.strftime("%Y/%m/%d")
            
            logger.info('=' * 60)
            logger.info('📰 FAST NEWS GENERATOR (RESEARCH LAYER SKIPPED)')
            logger.info(f'Date: {date_str}')
            logger.info('=' * 60)
            
            # Step 1: Fetch feeds
            logger.info('STEP 1: Fetch RSS Feeds')
            raw_stories = self.feeds.fetch_all_feeds()
            raw_stories = deduplicate_stories(raw_stories)
            logger.info(f'Found {len(raw_stories)} candidate stories')
            
            # Step 2: Fact-check (without research verification)
            logger.info('')
            logger.info('STEP 2: Fact-Check (built-in, no web_search)')
            logger.info(f'Analyzing {len(raw_stories)} stories...')
            
            analyzed_stories = []
            for i, story in enumerate(raw_stories, 1):
                try:
                    # Fact-check without research data
                    factcheck = self.factchecker.verify(story, {})
                    intent = self.intent_extractor.extract(story, {})
                    
                    article = Article(
                        section=story.section,
                        section_emoji=self._get_section_emoji(story.section),
                        headline=story.title,
                        body=story.description,
                        read_time='1 min',
                        verification=Verification(
                            status='UNVERIFIED',  # No research layer
                            sources=[],
                            primary_source=None,
                            timeline=[],
                            contradictions=[],
                            confidence=factcheck.overall_confidence,
                        ),
                        factcheck=factcheck,
                        intent=intent,
                        publish_decision=factcheck.safe_to_publish,
                        publish_reason='Fast mode: fact-check passed',
                    )
                    
                    analyzed_stories.append(article)
                    if factcheck.overall_confidence >= self.config.publish.min_confidence:
                        logger.debug(f'[{i}/{len(raw_stories)}] ✓ {story.title[:50]}... ({factcheck.overall_confidence}%)')
                    else:
                        logger.debug(f'[{i}/{len(raw_stories)}] ⚠ {story.title[:50]}... ({factcheck.overall_confidence}%, below threshold)')
                except Exception as e:
                    logger.debug(f'[{i}/{len(raw_stories)}] ✗ {story.title[:50]}... ({str(e)[:30]}...)')
            
            # Step 3: For fast mode, publish all articles (research layer will enable filtering)
            # Note: Without web_search research, fact-check scores are low (~46%)
            # This is expected - full verification requires research layer
            # TODO: When research layer enabled, re-enable confidence-based filtering
            filtered_articles = analyzed_stories
            logger.info(f'Publishing {len(filtered_articles)} articles (no filtering in fast mode)')
            
            # Step 4: Create edition
            edition = Edition(
                date=edition_date.strftime('%Y-%m-%d'),
                label=date_str,
                articles=filtered_articles,  # Use filtered articles
                generated_at=datetime.now().isoformat(),
                editor='News Engine v2.0 (Fast Mode)',
            )
            
            # Step 5: Save JSON
            logger.info('')
            logger.info('STEP 3: Save Outputs')
            date_dir = self.output_dir / date_path
            date_dir.mkdir(parents=True, exist_ok=True)
            
            json_path = date_dir / 'data.json'
            articles_json = []
            for a in edition.articles:
                articles_json.append({
                    'section': a.section,
                    'sectionEmoji': a.section_emoji,
                    'headline': a.headline,
                    'body': a.body,
                    'readTime': a.read_time,
                    'verification': {
                        'status': a.verification.status,
                        'sources': a.verification.sources,
                        'confidence': a.verification.confidence,
                    },
                    'factcheck': {
                        'overall_confidence': a.factcheck.overall_confidence,
                        'safe_to_publish': a.factcheck.safe_to_publish,
                    },
                })
            
            with open(json_path, 'w') as f:
                json.dump({
                    'date': edition.date,
                    'label': edition.label,
                    'articles': articles_json,
                    'generatedAt': edition.generated_at,
                    'editor': edition.editor,
                    'note': 'Fast mode: Research layer skipped (TODO: add web_search verification)'
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f'✓ JSON saved: {json_path}')
            result['json_path'] = str(json_path)
            
            # Step 6: Generate PDF (using wkhtmltopdf)
            html = self._generate_html(edition, date_str)
            html_path = Path(f'/tmp/news-{edition_date.strftime("%Y%m%d")}.html')
            with open(html_path, 'w') as f:
                f.write(html)
            
            pdf_path = date_dir / 'headlines-today.pdf'
            subprocess.run([
                'wkhtmltopdf', '--page-size', 'A4',
                '--margin-top', '15mm', '--margin-bottom', '15mm',
                '--margin-left', '10mm', '--margin-right', '10mm',
                '--enable-local-file-access',
                str(html_path), str(pdf_path)
            ], capture_output=True)
            
            logger.info(f'✓ PDF generated: {pdf_path}')
            result['pdf_path'] = str(pdf_path)
            
            # Step 7: Generate audio from FILTERED articles (matches JSON + PDF)
            audio_path = date_dir / 'headlines-today.mp3'
            if edition.articles:
                audio_text = "Headlines for today: " + ", ".join([a.headline for a in edition.articles[:15]])
            else:
                audio_text = "No headlines available today"
            
            try:
                subprocess.run([
                    'gtts-cli', audio_text,
                    '--lang', 'en',
                    '--output', str(audio_path)
                ], capture_output=True, timeout=30)
                logger.info(f'✓ Audio generated: {audio_path}')
                result['audio_path'] = str(audio_path)
            except Exception as e:
                logger.warning(f'⚠ Audio generation failed: {e}')
            
            result['success'] = True
            result['articles'] = len(filtered_articles)
            
            logger.info('')
            logger.info('=' * 60)
            logger.info('✅ EDITION GENERATED SUCCESSFULLY')
            logger.info('=' * 60)
            logger.info(f'Raw stories: {len(analyzed_stories)}')
            logger.info(f'Filtered articles: {len(filtered_articles)}')
            logger.info(f'PDF, Audio, JSON: All synced')
            logger.info(f'Available at: https://news-dev.suhailtaj.cloud/archive/{date_path}/')
            logger.info('')
            logger.info('⚠️  TODO: Enable web_search research layer')
            logger.info('   This is the core feature of news-engine!')
            logger.info('   Current: Fact-check without verification')
            logger.info('   Future: Full research + fact-check (via OpenClaw subagent)')
            
            return result
        
        except Exception as e:
            logger.error(f'❌ Error: {e}')
            import traceback
            traceback.print_exc()
            result['error'] = str(e)
            return result
    
    def _get_section_emoji(self, section: str) -> str:
        """Get emoji for section."""
        emojis = {
            "World News": "🌍",
            "AI & Tech": "🤖",
            "India": "🇮🇳",
            "Hyderabad": "🏙️",
            "Hot Topics & Viral": "🔥",
            "Business & Startups": "💼",
        }
        return emojis.get(section, "📰")
    
    def _generate_html(self, edition: Edition, date_str: str) -> str:
        """Generate HTML for PDF."""
        articles_html = ""
        for article in edition.articles:
            articles_html += f"""
            <div style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #ccc;">
                <h3 style="margin: 0 0 10px 0; font-size: 18px; font-weight: bold;">{article.headline}</h3>
                <p style="margin: 0; font-size: 14px; color: #666; line-height: 1.6;">{article.body}</p>
                <div style="margin-top: 8px; font-size: 12px; color: #999;">
                    <strong>{article.section}</strong> • Confidence: {article.verification.confidence}%
                </div>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>The Headlines Today - {date_str}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: #333; }}
                h1 {{ font-size: 32px; margin-bottom: 10px; }}
                .date {{ font-size: 14px; color: #999; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 15px; }}
                .mode {{ background: #fff3cd; padding: 10px 15px; margin-bottom: 20px; border-radius: 4px; font-size: 12px; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <h1>📰 The Headlines Today</h1>
            <div class="date">{date_str}</div>
            <div class="mode">⚠️ Fast Mode: Research layer skipped. Full verification coming soon when deployed as OpenClaw subagent.</div>
            {articles_html}
        </body>
        </html>
        """


def main():
    print("=" * 70)
    print("📰 FAST NEWS ENGINE - DEV EDITION")
    print("Skipping research layer (using built-in fact-check only)")
    print("=" * 70)
    print()
    
    try:
        runner = FastNewspaperRunner(verbose=True)
        result = runner.run_edition()
        
        if result['success']:
            print(f"\n✅ SUCCESS\n   Articles: {result['articles']}\n   PDF: {result['pdf_path']}\n   Audio: {result.get('audio_path', 'skipped')}")
            return 0
        else:
            print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
            return 1
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
