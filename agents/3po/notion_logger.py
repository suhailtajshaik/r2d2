#!/usr/bin/env python3
"""
Notion Session Logger
Structure: Session Log → "March 2026" → "15 March 2026" → content
"""

import urllib.request
import json
import ssl
import sys
import os
import argparse
from datetime import datetime

def _get_key():
    for p in ["/root/.config/notion/api_key", os.path.expanduser("~/.config/notion/api_key")]:
        if os.path.exists(p):
            return open(p).read().strip()
    return os.environ.get("NOTION_API_KEY", "")

NOTION_KEY = _get_key()
SESSION_LOG_PAGE = "323c2d43-b275-81ac-8718-c10dd413af23"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def notion_request(method, path, data=None):
    url = f"https://api.notion.com/v1{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers={
        "Authorization": f"Bearer {NOTION_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        return json.load(r)

def get_child_pages(parent_id):
    result = notion_request("GET", f"/blocks/{parent_id}/children")
    pages = {}
    for block in result.get("results", []):
        if block["type"] == "child_page":
            title = block["child_page"]["title"]
            pages[title] = block["id"]
    return pages

def create_page(parent_id, title, emoji="📅"):
    result = notion_request("POST", "/pages", {
        "parent": {"page_id": parent_id},
        "icon": {"type": "emoji", "emoji": emoji},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        }
    })
    return result["id"]

def append_content(page_id, blocks):
    notion_request("PATCH", f"/blocks/{page_id}/children", {"children": blocks})

def get_or_create_month_page(dt):
    # "March 2026"
    month_title = dt.strftime("%B %Y")
    children = get_child_pages(SESSION_LOG_PAGE)
    if month_title in children:
        return children[month_title]
    return create_page(SESSION_LOG_PAGE, month_title, "📆")

def get_or_create_day_page(month_page_id, dt):
    # "15 March 2026"
    day_title = dt.strftime("%-d %B %Y")
    children = get_child_pages(month_page_id)
    if day_title in children:
        return children[day_title]
    return create_page(month_page_id, day_title, "📅")

def get_day_page(date=None):
    dt = datetime.fromisoformat(date) if date else datetime.now()
    month_id = get_or_create_month_page(dt)
    return get_or_create_day_page(month_id, dt)

def log_entry(text, date=None):
    dt = datetime.fromisoformat(date) if date else datetime.now()
    day_id = get_day_page(date)
    timestamp = dt.strftime("%H:%M UTC")
    append_content(day_id, [{
        "object": "block", "type": "paragraph",
        "paragraph": {"rich_text": [
            {"type": "text", "text": {"content": f"[{timestamp}] "}, "annotations": {"color": "gray"}},
            {"type": "text", "text": {"content": text}}
        ]}
    }])
    return day_id

def log_heading(text, date=None):
    day_id = get_day_page(date)
    append_content(day_id, [{
        "object": "block", "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]}
    }])
    return day_id

def log_bullets(items, date=None):
    day_id = get_day_page(date)
    append_content(day_id, [{
        "object": "block", "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": item}}]}
    } for item in items])
    return day_id

def log_divider(date=None):
    day_id = get_day_page(date)
    append_content(day_id, [{"object": "block", "type": "divider", "divider": {}}])
    return day_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", help="Log entry text")
    parser.add_argument("--heading", help="Log a heading")
    parser.add_argument("--bullets", nargs="+", help="Log bullet points")
    parser.add_argument("--divider", action="store_true")
    parser.add_argument("--date", help="Date YYYY-MM-DD, defaults to today")
    args = parser.parse_args()

    if args.log:
        print(f"Logged ✓ → {log_entry(args.log, args.date)}")
    elif args.heading:
        print(f"Heading ✓ → {log_heading(args.heading, args.date)}")
    elif args.bullets:
        print(f"Bullets ✓ → {log_bullets(args.bullets, args.date)}")
    elif args.divider:
        print(f"Divider ✓ → {log_divider(args.date)}")
    else:
        parser.print_help()
