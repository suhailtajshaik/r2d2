#!/usr/bin/env python3
"""
The Headlines Today — Daily Newspaper Generator
R2D2 orchestrates: Maxwell edits → PDF generated → Audio created → Sent to Suhail
"""

import subprocess
import sys
import json
import os
from datetime import datetime

def generate_html_from_articles(articles, date_str, day_str):
    """Generate newspaper HTML from Maxwell's edited articles."""
    
    # Group by section
    sections_order = ["World News", "AI & Tech", "India", "Hyderabad", "Hot Topics & Viral", "Business & Startups"]
    section_emojis = {
        "World News": "🌍",
        "AI & Tech": "🤖",
        "India": "🇮🇳",
        "Hyderabad": "🏙️",
        "Hot Topics & Viral": "🔥",
        "Business & Startups": "💼"
    }
    
    grouped = {}
    for article in articles:
        s = article.get("section", "World News")
        if s not in grouped:
            grouped[s] = []
        grouped[s].append(article)

    sections_html = ""
    for section in sections_order:
        if section not in grouped:
            continue
        emoji = section_emojis.get(section, "📰")
        articles_html = ""
        for a in grouped[section][:4]:
            headline = a.get("headline", "")
            body = a.get("body", a.get("lede", ""))
            kicker = a.get("kicker", "")
            articles_html += f"""
    <div class="article">
      <div class="article-headline">{headline}</div>
      <div class="article-body">{body}</div>
      {f'<div class="article-kicker">▶ {kicker}</div>' if kicker else ''}
    </div>"""
        
        sections_html += f"""
<div class="section">
  <div class="section-header">{emoji} {section}</div>
  {articles_html}
</div>
<hr class="divider">"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>The Headlines Today — {date_str}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Serif+4:wght@400;600&family=Inter:wght@400;500;600&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Source Serif 4', Georgia, serif;
    background: #fff; color: #1a1a1a;
    font-size: 18px; line-height: 1.7;
    max-width: 900px; margin: 0 auto; padding: 40px 30px;
  }}
  .masthead {{
    text-align: center;
    border-top: 5px solid #1a1a1a; border-bottom: 5px solid #1a1a1a;
    padding: 20px 0 16px; margin-bottom: 8px;
  }}
  .masthead h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 60px; font-weight: 900; letter-spacing: -1px; line-height: 1; margin-bottom: 6px;
  }}
  .tagline {{ font-family: 'Inter', sans-serif; font-size: 13px; letter-spacing: 3px; text-transform: uppercase; color: #555; margin-bottom: 10px; }}
  .date-line {{
    font-family: 'Inter', sans-serif; font-size: 13px; color: #555;
    display: flex; justify-content: space-between;
    border-top: 1px solid #ccc; padding-top: 8px;
  }}
  .greeting {{
    font-family: 'Inter', sans-serif; font-size: 15px; color: #555;
    text-align: center; padding: 12px 0; border-bottom: 1px solid #ddd;
    margin-bottom: 30px; font-style: italic;
  }}
  .section {{ margin-bottom: 36px; }}
  .section-header {{
    font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 600;
    letter-spacing: 4px; text-transform: uppercase;
    color: #fff; background: #1a1a1a; padding: 6px 14px; margin-bottom: 20px; display: inline-block;
  }}
  .article {{ margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #e5e5e5; }}
  .article:last-child {{ border-bottom: none; }}
  .article-headline {{
    font-family: 'Playfair Display', serif; font-size: 24px; font-weight: 700;
    line-height: 1.3; margin-bottom: 10px; color: #111;
  }}
  .article-body {{ font-size: 17px; line-height: 1.75; color: #333; margin-bottom: 8px; }}
  .article-kicker {{ font-size: 15px; color: #666; font-style: italic; border-left: 3px solid #1a1a1a; padding-left: 12px; }}
  hr.divider {{ border: none; border-top: 1px solid #ddd; margin: 30px 0; }}
  .footer {{
    margin-top: 40px; border-top: 3px solid #1a1a1a; padding-top: 16px;
    display: flex; justify-content: space-between;
    font-family: 'Inter', sans-serif; font-size: 13px; color: #777;
  }}
  .editor-badge {{
    font-family: 'Inter', sans-serif; font-size: 11px; color: #999;
    text-align: center; margin-top: 8px;
  }}
</style>
</head>
<body>

<div class="masthead">
  <div class="tagline">Independent · Daily · Digital</div>
  <h1>The Headlines Today</h1>
  <div class="date-line">
    <span>EST. 2026</span>
    <span>{day_str.upper()}, {date_str.upper()}</span>
    <span>FREE TO READ</span>
  </div>
</div>
<div class="editor-badge">Edited by Maxwell · Compiled by R2D2</div>

<div class="greeting">Your daily briefing — world news, tech, India, Hyderabad, and what's trending.</div>

{sections_html}

<div class="footer">
  <span>The Headlines Today</span>
  <span>{date_str}</span>
  <span>Stay informed.</span>
</div>
</body>
</html>"""


def generate_audio(articles, date_file, archive_dir):
    """Generate audio briefing from Maxwell's articles — all headlines, all sections."""
    from gtts import gTTS
    from datetime import datetime

    now = datetime.now()
    date_spoken = now.strftime("%A, %B %d, %Y")

    lines = [
        f"The Headlines Today. {date_spoken}.",
        "Edited by Maxwell. Here are today's headlines.",
    ]

    sections_order = ["World News", "AI & Tech", "India", "Hyderabad", "Hot Topics & Viral", "Business & Startups"]

    for section in sections_order:
        section_articles = [a for a in articles if a.get("section") == section]
        if not section_articles:
            continue
        lines.append(f"{section}.")
        for a in section_articles:
            headline = a.get("headline", "").strip()
            lede = a.get("lede", a.get("body", ""))[:300].strip()
            kicker = a.get("kicker", "").strip()
            lines.append(f"{headline}. {lede}")
            if kicker:
                lines.append(kicker)
        lines.append("")  # brief pause between sections

    lines.append("That's all for today. Stay informed. The Headlines Today.")

    spoken = " ".join(lines)
    # Clean up any HTML entities or stray characters
    spoken = (spoken
        .replace("&amp;", "and")
        .replace("&", "and")
        .replace("<", "")
        .replace(">", "")
        .replace("▶", "")
        .replace("▹", "")
        .strip()
    )

    audio_path = f"/tmp/headlines-{date_file}.mp3"
    tts = gTTS(text=spoken, lang='en', tld='co.in')
    tts.save(audio_path)

    archive_audio = f"{archive_dir}/headlines-today.mp3"
    subprocess.run(["cp", audio_path, archive_audio])
    print(f"✅ Audio saved to archive — {len(articles)} articles across {len(sections_order)} sections")
    return audio_path


def main():
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    day_str = now.strftime("%A")
    date_file = now.strftime("%Y-%m-%d")
    date_path = now.strftime("%Y/%m/%d")
    archive_dir = f"/home/r2d2/newspapers/{date_path}"
    os.makedirs(archive_dir, exist_ok=True)

    print(f"📰 The Headlines Today — {date_str}")
    print(f"🤖 R2D2 orchestrating Maxwell...\n")

    # Step 1: Call Maxwell to fetch + edit
    result = subprocess.run(
        ["python3", "/home/r2d2/tools/editor-agent/maxwell.py"],
        capture_output=False, text=True, timeout=600
    )

    # Step 2: Load Maxwell's output
    data_json = f"{archive_dir}/data.json"
    if not os.path.exists(data_json):
        print("❌ Maxwell didn't produce data.json — aborting")
        sys.exit(1)

    with open(data_json) as f:
        data = json.load(f)
    articles = data.get("articles", [])
    print(f"\n📝 {len(articles)} articles from Maxwell")

    # Step 3: Generate HTML + PDF
    html = generate_html_from_articles(articles, date_str, day_str)
    html_path = f"/tmp/headlines-{date_file}.html"
    pdf_path = f"/tmp/headlines-{date_file}.pdf"

    with open(html_path, 'w') as f:
        f.write(html)

    subprocess.run([
        'wkhtmltopdf', '--page-size', 'A4',
        '--margin-top', '15mm', '--margin-bottom', '15mm',
        '--margin-left', '10mm', '--margin-right', '10mm',
        '--enable-local-file-access',
        html_path, pdf_path
    ], capture_output=True)

    subprocess.run(['cp', pdf_path, f"{archive_dir}/headlines-today.pdf"])
    print(f"✅ PDF generated and archived")

    # Step 4: Generate audio
    audio_path = generate_audio(articles, date_file, archive_dir)

    # Step 5: Rebuild news-site index
    subprocess.run(['bash', '/home/r2d2/projects/news-site/scripts/generate-index.sh'])
    print(f"✅ News site index updated")

    # Step 6: Send PDF via WhatsApp
    ws_pdf = f"/home/r2d2/.openclaw/workspace/headlines-{date_file}.pdf"
    subprocess.run(['cp', pdf_path, ws_pdf])
    subprocess.run([
        'openclaw', 'message', 'send', '--channel', 'whatsapp',
        '--target', '+14699941765',
        '--media', ws_pdf,
        '--message', f"📰 The Headlines Today — {date_str}\nEdited by Maxwell · {len(articles)} stories"
    ])
    os.remove(ws_pdf)

    # Step 7: Send audio via WhatsApp
    ws_audio = f"/home/r2d2/.openclaw/workspace/headlines-{date_file}.mp3"
    subprocess.run(['cp', audio_path, ws_audio])
    subprocess.run([
        'openclaw', 'message', 'send', '--channel', 'whatsapp',
        '--target', '+14699941765',
        '--media', ws_audio,
        '--message', "🎙️ Audio briefing — The Headlines Today"
    ])
    os.remove(ws_audio)

    print(f"\n✅ The Headlines Today — DONE")
    print(f"   PDF + Audio sent to WhatsApp")
    print(f"   Archive: {archive_dir}")

if __name__ == '__main__':
    main()
