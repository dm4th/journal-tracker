#!/usr/bin/env python3
"""
Journal Gaps - Find missing dates in journal entries

Queries Notion for all journal entry dates and identifies gaps.

Usage:
    python3 journal_gaps.py [--days=N]

Options:
    --days=N    Only look back N days from today (default: all entries)
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from typing import List, Set

def get_all_journal_dates(token: str, database_id: str, days_back: int = None) -> Set[str]:
    """Fetch all journal entry dates from Notion."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    # Build filter for date range if specified
    payload = {
        "sorts": [{"property": "Date", "direction": "descending"}]
    }

    if days_back:
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        payload["filter"] = {
            "property": "Date",
            "date": {"on_or_after": start_date}
        }

    all_dates = set()
    has_more = True
    next_cursor = None

    while has_more:
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        for entry in data.get('results', []):
            date = entry.get('properties', {}).get('Date', {}).get('date', {})
            if date and date.get('start'):
                all_dates.add(date['start'])

        has_more = data.get('has_more', False)
        next_cursor = data.get('next_cursor')

    return all_dates

def find_gaps(dates: Set[str], days_back: int = None) -> List[str]:
    """Find missing dates between earliest and latest entry."""
    if not dates:
        return []

    sorted_dates = sorted(dates)
    start_date = datetime.strptime(sorted_dates[0], "%Y-%m-%d")

    if days_back:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")

    missing = []
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        if date_str not in dates:
            missing.append(date_str)
        current += timedelta(days=1)

    return missing

def main():
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_JOURNAL_DATABASE_ID')

    if not token or not database_id:
        print("Error: Set NOTION_TOKEN and NOTION_JOURNAL_DATABASE_ID", file=sys.stderr)
        return 1

    # Parse --days flag
    days_back = None
    for arg in sys.argv:
        if arg.startswith('--days='):
            try:
                days_back = int(arg.split('=')[1])
            except ValueError:
                pass

    print("Fetching journal dates from Notion...")
    dates = get_all_journal_dates(token, database_id, days_back)

    if not dates:
        print("No journal entries found.")
        return 0

    print(f"Found {len(dates)} journal entries.")

    gaps = find_gaps(dates, days_back)

    if not gaps:
        print("No missing dates!")
        return 0

    print(f"\nMissing {len(gaps)} journal entries:")
    for date in gaps:
        # Format nicely with day of week
        dt = datetime.strptime(date, "%Y-%m-%d")
        print(f"  - {date} ({dt.strftime('%A')})")

    return 0

if __name__ == "__main__":
    sys.exit(main())
