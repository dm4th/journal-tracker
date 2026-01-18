#!/usr/bin/env python3
"""
Monthly Review Analyzer - Generate monthly progress reports against goals

Usage:
    python3 monthly_analyze.py [--month=YYYY-MM] [--year=YYYY]

Options:
    --month=YYYY-MM    Analyze specific month (default: previous month)
    --year=YYYY        Analyze full year (generates all months)

Outputs JSON with goal progress and statistics.
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from calendar import monthrange
from pathlib import Path
import re

def get_month_range(year: int, month: int):
    """Get start and end dates for a month."""
    _, last_day = monthrange(year, month)
    start = f"{year}-{month:02d}-01"
    end = f"{year}-{month:02d}-{last_day:02d}"
    return start, end

def query_entries(token: str, database_id: str, start_date: str, end_date: str):
    """Fetch journal entries for a date range."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {
        "filter": {
            "and": [
                {"property": "Date", "date": {"on_or_after": start_date}},
                {"property": "Date", "date": {"on_or_before": end_date}}
            ]
        },
        "sorts": [{"property": "Date", "direction": "ascending"}],
        "page_size": 100
    }

    all_results = []
    has_more = True
    next_cursor = None

    while has_more:
        if next_cursor:
            payload["start_cursor"] = next_cursor
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        all_results.extend(data.get('results', []))
        has_more = data.get('has_more', False)
        next_cursor = data.get('next_cursor')

    return all_results

def load_goals():
    """Load goals configuration."""
    script_dir = Path(__file__).parent.parent
    goals_file = script_dir / "goals-2026.json"

    if goals_file.exists():
        with open(goals_file) as f:
            return json.load(f)
    return None

def analyze_entries(entries, goals_config):
    """Analyze entries against goals."""
    results = {
        "entry_count": len(entries),
        "scores": [],
        "events": {},
        "locations": {},
        "highlights": [],
        "lowlights": [],
        "goal_progress": {},
        "qualitative": {}
    }

    # Initialize event counters from goals
    if goals_config:
        for category, goals in goals_config.get("goals", {}).items():
            for goal_key, goal in goals.items():
                if "event_patterns" in goal:
                    results["goal_progress"][goal_key] = {
                        "name": goal["name"],
                        "count": 0,
                        "target": goal.get("target_monthly", 0),
                        "description": goal.get("description", "")
                    }

        # Initialize qualitative tracking
        for key in goals_config.get("qualitative_keywords", {}):
            results["qualitative"][key] = {"count": 0, "entries": []}

    for entry in entries:
        props = entry.get('properties', {})
        date = props.get('Date', {}).get('date', {}).get('start', '')

        # Score
        score_select = props.get('Score', {}).get('select', {})
        if score_select:
            try:
                results["scores"].append(int(score_select.get('name', '0')))
            except:
                pass

        # Events
        events = props.get('Events', {}).get('multi_select', [])
        for e in events:
            name = e.get('name', '')
            results["events"][name] = results["events"].get(name, 0) + 1

            # Check against goal patterns
            if goals_config:
                for category, goals in goals_config.get("goals", {}).items():
                    for goal_key, goal in goals.items():
                        patterns = goal.get("event_patterns", [])
                        for pattern in patterns:
                            if pattern in name:
                                results["goal_progress"][goal_key]["count"] += 1
                                break

        # Location
        loc = props.get('Location', {}).get('select', {})
        if loc:
            loc_name = loc.get('name', 'Unknown')
            results["locations"][loc_name] = results["locations"].get(loc_name, 0) + 1

        # Highlights/Lowlights
        highlight = props.get('Highlight', {}).get('rich_text', [])
        highlight_text = ''.join([t.get('plain_text', '') for t in highlight])
        if highlight_text.strip():
            results["highlights"].append({"date": date, "text": highlight_text.strip()})

        lowlight = props.get('Lowlight', {}).get('rich_text', [])
        lowlight_text = ''.join([t.get('plain_text', '') for t in lowlight])
        if lowlight_text.strip():
            results["lowlights"].append({"date": date, "text": lowlight_text.strip()})

        # Qualitative keyword search
        all_text = (highlight_text + ' ' + lowlight_text).lower()
        if goals_config:
            for key, keywords in goals_config.get("qualitative_keywords", {}).items():
                for kw in keywords:
                    if kw in all_text:
                        results["qualitative"][key]["count"] += 1
                        results["qualitative"][key]["entries"].append({"date": date, "snippet": all_text[:100]})
                        break

    # Calculate score statistics
    if results["scores"]:
        results["score_stats"] = {
            "average": round(sum(results["scores"]) / len(results["scores"]), 2),
            "min": min(results["scores"]),
            "max": max(results["scores"]),
            "positive_days": len([s for s in results["scores"] if s > 0]),
            "negative_days": len([s for s in results["scores"] if s < 0]),
            "neutral_days": len([s for s in results["scores"] if s == 0])
        }

        total = len(results["scores"])
        results["score_stats"]["positive_pct"] = round(results["score_stats"]["positive_days"] / total * 100, 1)
        results["score_stats"]["negative_pct"] = round(results["score_stats"]["negative_days"] / total * 100, 1)

    # Calculate goal status
    for goal_key, progress in results["goal_progress"].items():
        if progress["target"] > 0:
            pct = round(progress["count"] / progress["target"] * 100, 1)
            progress["percentage"] = pct
            if pct >= 100:
                progress["status"] = "ON_TRACK"
            elif pct >= 75:
                progress["status"] = "CLOSE"
            elif pct >= 50:
                progress["status"] = "NEEDS_ATTENTION"
            else:
                progress["status"] = "OFF_TRACK"

    # Add journaling goal
    if goals_config and "consistency" in goals_config.get("goals", {}):
        journal_goal = goals_config["goals"]["consistency"].get("journaling", {})
        target = journal_goal.get("target_monthly", 28)
        pct = round(len(entries) / target * 100, 1)
        results["goal_progress"]["journaling"] = {
            "name": "Journal Entries",
            "count": len(entries),
            "target": target,
            "percentage": pct,
            "status": "ON_TRACK" if pct >= 100 else "CLOSE" if pct >= 90 else "NEEDS_ATTENTION" if pct >= 75 else "OFF_TRACK"
        }

    return results

def main():
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_JOURNAL_DATABASE_ID')

    if not token or not database_id:
        print(json.dumps({"error": "Set NOTION_TOKEN and NOTION_JOURNAL_DATABASE_ID"}))
        return 1

    # Parse arguments
    target_month = None
    target_year = None

    for arg in sys.argv:
        if arg.startswith('--month='):
            target_month = arg.split('=')[1]
        elif arg.startswith('--year='):
            target_year = int(arg.split('=')[1])

    # Default to previous month
    if not target_month and not target_year:
        today = datetime.now()
        first_of_month = today.replace(day=1)
        prev_month = first_of_month - timedelta(days=1)
        target_month = prev_month.strftime("%Y-%m")

    goals_config = load_goals()

    if target_year:
        # Full year analysis
        all_months = []
        for month in range(1, 13):
            start, end = get_month_range(target_year, month)
            entries = query_entries(token, database_id, start, end)
            if entries:
                analysis = analyze_entries(entries, goals_config)
                analysis["month"] = f"{target_year}-{month:02d}"
                all_months.append(analysis)
        print(json.dumps({"year": target_year, "months": all_months}, indent=2))
    else:
        # Single month analysis
        year, month = map(int, target_month.split('-'))
        start, end = get_month_range(year, month)
        entries = query_entries(token, database_id, start, end)
        analysis = analyze_entries(entries, goals_config)
        analysis["month"] = target_month
        analysis["period"] = {"start": start, "end": end}
        print(json.dumps(analysis, indent=2))

    return 0

if __name__ == "__main__":
    sys.exit(main())
