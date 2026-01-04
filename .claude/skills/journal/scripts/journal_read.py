#!/usr/bin/env python3
"""
Journal Read - Export entries needing AI enhancement

Pulls entries from Notion marked for AI touchup and outputs them
in a structured format for Claude to enhance.

Usage:
    python3 scripts/journal_read.py [--limit=N]
"""

import os
import sys
import json
import requests
from typing import List, Dict

def get_entries_for_touchup(token: str, database_id: str, limit: int = None) -> List[Dict]:
    """Fetch entries marked for AI touchup from Notion."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {
        "filter": {
            "property": "AI Touchup",
            "checkbox": {"equals": True}
        },
        "sorts": [
            {"property": "Date", "direction": "descending"}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    entries = response.json().get('results', [])

    if limit:
        entries = entries[:limit]

    return entries

def extract_entry_data(entry: Dict) -> Dict:
    """Extract relevant fields from a Notion entry."""
    props = entry['properties']

    def get_text(prop_name: str) -> str:
        prop = props.get(prop_name, {})
        rich_text = prop.get('rich_text', [])
        return rich_text[0]['plain_text'] if rich_text else ""

    def get_select(prop_name: str) -> str:
        prop = props.get(prop_name, {})
        select = prop.get('select')
        return select.get('name', '') if select else ""

    def get_multi_select(prop_name: str) -> List[str]:
        prop = props.get(prop_name, {})
        options = prop.get('multi_select', [])
        return [o['name'] for o in options]

    return {
        'page_id': entry['id'],
        'date': props.get('Date', {}).get('date', {}).get('start', ''),
        'current_title': props.get('Name', {}).get('title', [{}])[0].get('plain_text', '') if props.get('Name', {}).get('title') else '',
        'description': get_text('Description'),
        'highlight': get_text('Highlight'),
        'lowlight': get_text('Lowlight'),
        'location': get_select('Location'),
        'events': get_multi_select('Events'),
        'score': get_select('Score'),
        'anxiety': get_select('Anxiety'),
        'depression': get_select('Depression'),
    }

def main():
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_JOURNAL_DATABASE_ID')

    if not token or not database_id:
        print("Error: Set NOTION_TOKEN and NOTION_JOURNAL_DATABASE_ID", file=sys.stderr)
        return 1

    # Parse limit flag
    limit = None
    for arg in sys.argv:
        if arg.startswith('--limit='):
            try:
                limit = int(arg.split('=')[1])
            except ValueError:
                pass

    entries = get_entries_for_touchup(token, database_id, limit)

    if not entries:
        print("No entries found for AI touchup.")
        return 0

    extracted = [extract_entry_data(e) for e in entries]

    # Output as JSON for easy parsing
    print(json.dumps(extracted, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
