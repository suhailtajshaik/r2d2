#!/usr/bin/env python3
"""
Notion Session Logger
Structure: Session Log → Month sub-page → Day sub-page → content

Usage:
  python3 notion_logger.py --log "Your log entry text"
  python3 notion_logger.py --log "Entry" --date 2026-03-15
"""

import urllib.request
import json
import ssl
import sys
import os
import argparse
from datetime import datetime

NOTION_KEY = open("/root/.config/notion/api_key").read().strip() if os.path.exists("/root/.config/notion/api_key") else \
             open(os.path.expanduser("~/.config/notion/api_key")).read().strip()
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
    """Get all child pages of a page."""
    result = notion_request("GET", f"/blocks/{parent_id}/children")
    pages = {}
    for block in result.get("results", []):
        if block["type"] == "child_page":
            title = block["child_page"]["title"]
            pages[title] = block["id"]
    return pages

def create_page(parent_id, title, emoji="📅"):
    """Create a new sub-page."""
    result = notion_request("POST", "/pages", {
        "parent": {"page_id": parent_id},
        "icon": {"type": "emoji", "emoji": emoji},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        }
    })
    return result["id"]

def append_content(page_id, blocks):
    """Append blocks to a page."""
    notion_request("PATCH", f"/blocks/{page_id}/children", {"children": blocks})

def get_or_create_month_page(month_str, month_label):
    """Get or create the month sub-page under Session Log."""
    children = get_child_pages(SESSION_LOG_PAGE)
    if month_str in children:
        return children[month_str]
    return create_page(SESSION_LOG_PAGE, month_str, "📆")

def get_or_create_day_page(month_page_id, day_str, day_label):
    """Get or create the day sub-page under the month page."""
    children = get_child_pages(month_page_id)
    if day_str in children:
        return children[day_str]
    return create_page(month_page_id, day_str, "📅")

def log_entry(text, date=None):
    """Log an entry to the correct month/day page."""
    dt = datetime.fromisoformat(date) if date else datetime.now()
    
    month_str = dt.strftime("%Y-%m — %B %Y")       # "2026-03 — March 2026"
    day_str = dt.strftime("%Y-%m-%d — %A")          # "2026-03-15 — Sunday"
    month_key = dt.strftime("%Y-%m — %B %Y")
    day_key = dt.strftime("%Y-%m-%d — %A")
    
    # Get or create month page
    month_id = get_or_create_month_page(month_key, month_str)
    
    # Get or create day page
    day_id = get_or_create_day_page(month_id, day_key, day_str)
    
    # Append log entry to day page
    timestamp = dt.strftime("%H:%M UTC")
    blocks = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": f"[{timestamp}] "}, "annotations": {"color": "gray"}},
                    {"type": "text", "text": {"content": text}}
                ]
            }
        }
    ]
    append_content(day_id, blocks)
    return day_id

def log_heading(text, date=None):
    """Log a heading to the day page."""
    dt = datetime.fromisoformat(date) if date else datetime.now()
    month_key = dt.strftime("%Y-%m — %B %Y")
    day_key = dt.strftime("%Y-%m-%d — %A")
    
    month_id = get_or_create_month_page(month_key, month_key)
    day_id = get_or_create_day_page(month_id, day_key, day_key)
    
    blocks = [{
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]}
    }]
    append_content(day_id, blocks)
    return day_id

def log_bullets(items, date=None):
    """Log bullet points to the day page."""
    dt = datetime.fromisoformat(date) if date else datetime.now()
    month_key = dt.strftime("%Y-%m — %B %Y")
    day_key = dt.strftime("%Y-%m-%d — %A")
    
    month_id = get_or_create_month_page(month_key, month_key)
    day_id = get_or_create_day_page(month_id, day_key, day_key)
    
    blocks = [{
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": item}}]}
    } for item in items]
    
    append_content(day_id, blocks)
    return day_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log to Notion Session Log")
    parser.add_argument("--log", help="Log entry text")
    parser.add_argument("--heading", help="Log a heading")
    parser.add_argument("--bullets", nargs="+", help="Log bullet points")
    parser.add_argument("--date", help="Date (YYYY-MM-DD), defaults to today")
    args = parser.parse_args()

    if args.log:
        day_id = log_entry(args.log, args.date)
        print(f"Logged ✓ → {day_id}")
    elif args.heading:
        day_id = log_heading(args.heading, args.date)
        print(f"Heading logged ✓ → {day_id}")
    elif args.bullets:
        day_id = log_bullets(args.bullets, args.date)
        print(f"Bullets logged ✓ → {day_id}")
    else:
        parser.print_help()
