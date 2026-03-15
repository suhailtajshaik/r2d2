#!/usr/bin/env python3
"""
Maxwell — The Editor Agent
Takes raw news research and produces clean, publication-ready JSON articles.
Works alongside R2D2 like 3PO — called when needed.
"""

import subprocess
import json
import sys
import os
from datetime import datetime

EDITOR_PROMPT = open(os.path.join(os.path.dirname(__file__), "EDITOR.md")).read()

def fetch_raw_news():
    """Fetch raw news from all RSS sources."""
    sources = {
        "World News": [
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://feeds.reuters.com/reuters/topNews",
        ],
        "AI & Tech": [
            "https://hnrss.org/frontpage",
            "https://feeds.bbci.co.uk/news/technology/rss.xml",
        ],
        "India": [
            "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        ],
        "Hyderabad": [
            "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
        ],
        "Hot Topics & Viral": [
            "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
            "https://hnrss.org/frontpage",
        ],
        "Business & Startups": [
            "https://feeds.bbci.co.uk/news/business/rss.xml",
        ],
    }

    import xml.etree.ElementTree as ET
    import urllib.request, ssl

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    raw = {}
    for section, urls in sources.items():
        items = []
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
                    content = r.read().decode("utf-8", errors="ignore")
                root = ET.fromstring(content)
                for item in root.findall(".//item")[:6]:
                    import re
                    title = (item.findtext("title") or "").strip()
                    desc = (item.findtext("description") or "").strip()
                    desc = re.sub(r'<[^>]+>', '', desc)
                    desc = re.sub(r'\s+', ' ', desc).strip()
                    if title:
                        items.append(f"HEADLINE: {title}\nSUMMARY: {desc[:400]}")
            except Exception as e:
                continue
        raw[section] = "\n\n".join(items[:6]) if items else "No data available"
    return raw

def run_maxwell(raw_news, date_str):
    """Pass raw news through Maxwell (Claude) for editing."""
    
    raw_text = ""
    for section, content in raw_news.items():
        raw_text += f"\n\n=== {section} ===\n{content}"

    prompt = f"""{EDITOR_PROMPT}

---

Today's date: {date_str}

Here is the raw research to edit into clean articles:

{raw_text}

---

Transform all of this into clean, publication-ready articles following your editorial standards exactly.
Return ONLY a valid JSON array. No preamble, no explanation, just the JSON.
"""

    print("✏️  Maxwell is editing...")
    result = subprocess.run(
        ["claude", "--permission-mode", "bypassPermissions", "--print", prompt],
        capture_output=True, text=True, timeout=300
    )
    
    output = result.stdout.strip()
    
    # Extract JSON from output
    import re
    json_match = re.search(r'\[.*\]', output, re.DOTALL)
    if json_match:
        try:
            articles = json.loads(json_match.group())
            print(f"✅ Maxwell produced {len(articles)} clean articles")
            return articles
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"Raw output: {output[:500]}")
            return None
    else:
        print(f"❌ No JSON found in Maxwell's output")
        print(f"Raw output: {output[:500]}")
        return None

def save_articles(articles, date_path, date_file):
    """Save edited articles as data.json in the archive."""
    archive_dir = f"/home/r2d2/newspapers/{date_path}"
    os.makedirs(archive_dir, exist_ok=True)
    
    data = {
        "date": date_file,
        "label": datetime.now().strftime("%A, %B %d, %Y"),
        "articles": articles,
        "generatedAt": datetime.now().isoformat(),
        "editor": "Maxwell v1.0"
    }
    
    output_path = f"{archive_dir}/data.json"
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Articles saved to {output_path}")
    return output_path

def main():
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    date_file = now.strftime("%Y-%m-%d")
    date_path = now.strftime("%Y/%m/%d")

    print(f"📰 Maxwell — The Headlines Today Editor")
    print(f"📅 Date: {date_str}")
    print()

    print("📡 Fetching raw news from RSS sources...")
    raw_news = fetch_raw_news()
    for section, content in raw_news.items():
        count = content.count("HEADLINE:")
        print(f"  {section}: {count} raw items")

    articles = run_maxwell(raw_news, date_str)
    
    if articles:
        save_articles(articles, date_path, date_file)
        print(f"\n✅ Maxwell done — {len(articles)} articles ready for publication")
        return articles
    else:
        print("\n❌ Maxwell failed to produce articles")
        return None

if __name__ == "__main__":
    main()
