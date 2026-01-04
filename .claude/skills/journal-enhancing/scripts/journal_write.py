#!/usr/bin/env python3
"""
Journal Write - Push enhanced entries back to Notion

Takes enhanced journal content and updates Notion pages.

Usage:
    python3 scripts/journal_write.py '<json_data>'

    JSON format:
    {
        "page_id": "xxx-xxx-xxx",
        "title": "Creative Title Here",
        "emoji": "🎉",
        "description": "Enhanced narrative description..."
    }

    Or for multiple entries:
    [
        {"page_id": "...", "title": "...", "emoji": "...", "description": "..."},
        ...
    ]
"""

import os
import sys
import json
import requests

def update_entry(token: str, page_id: str, title: str, emoji: str, description: str) -> bool:
    """Update a Notion page with enhanced content."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Name": {
                "title": [{"type": "text", "text": {"content": title}}]
            },
            "Description": {
                "rich_text": [{"type": "text", "text": {"content": description}}]
            },
            "AI Touchup": {
                "checkbox": False
            }
        },
        "icon": {
            "type": "emoji",
            "emoji": emoji
        }
    }

    response = requests.patch(url, headers=headers, json=payload)
    response.raise_for_status()
    return True

def main():
    token = os.getenv('NOTION_TOKEN')

    if not token:
        print("Error: Set NOTION_TOKEN environment variable", file=sys.stderr)
        return 1

    if len(sys.argv) < 2:
        print("Usage: python3 journal_write.py '<json_data>'", file=sys.stderr)
        print("  JSON should have: page_id, title, emoji, description", file=sys.stderr)
        return 1

    try:
        data = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return 1

    # Handle single entry or list of entries
    entries = data if isinstance(data, list) else [data]

    for entry in entries:
        page_id = entry.get('page_id')
        title = entry.get('title')
        emoji = entry.get('emoji')
        description = entry.get('description')

        if not all([page_id, title, emoji, description]):
            print(f"Skipping incomplete entry: {entry}", file=sys.stderr)
            continue

        try:
            update_entry(token, page_id, title, emoji, description)
            print(f"Updated: {title} {emoji}")
        except Exception as e:
            print(f"Error updating {page_id}: {e}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    sys.exit(main())
