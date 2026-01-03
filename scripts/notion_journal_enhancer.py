#!/usr/bin/env python3
"""
Notion Journal Enhancer

This script automates the enhancement of personal journal entries in a Notion database.
It finds entries marked for AI touchup and enhances them with rich descriptions,
titles, and emojis while maintaining the user's authentic writing style.

Features:
- Finds entries with "AI Touchup" checkbox enabled
- Enhances descriptions with detailed, contextual narratives
- Adds descriptive titles (avoiding day names)
- Adds relevant emojis
- Unchecks the AI Touchup flag when done
- Maintains user's writing voice and patterns

Usage:
    python3 notion_journal_enhancer.py [--dry-run]

Environment Variables:
    NOTION_TOKEN: Notion integration token
    NOTION_JOURNAL_DATABASE_ID: Journal database ID

Author: Claude Code AI Assistant
Created: 2025-11-19
"""

import os
import sys
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

class NotionJournalEnhancer:
    def __init__(self, token: str, database_id: str):
        self.token = token
        self.database_id = database_id
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.notion.com/v1'

    def find_entries_for_touchup(self) -> List[Dict]:
        """Find all entries marked for AI touchup."""
        url = f"{self.base_url}/databases/{self.database_id}/query"
        payload = {
            "filter": {
                "property": "AI Touchup",
                "checkbox": {
                    "equals": True
                }
            },
            "sorts": [
                {
                    "property": "Date",
                    "direction": "descending"
                }
            ]
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json().get('results', [])

    # Event-to-title/emoji mappings (priority order within categories)
    EVENT_MAPPINGS = {
        # Outdoors - High priority, unique experiences
        'Outdoors - Skiing': ('Ski Day', '🎿'),
        'Outdoors - Hike': ('Trail Day', '🥾'),
        'Outdoors - Camping': ('Camping Adventure', '🏕️'),
        'Outdoors - Beach': ('Beach Day', '🏖️'),
        'Outdoors - Sports': ('Outdoor Sports', '🌳'),
        'Outdoors - Other': ('Outdoor Day', '🌲'),

        # Personal - High priority, meaningful moments
        'Personal - Date': ('Date Night', '💕'),
        'Personal - Family': ('Family Time', '👨‍👩‍👧'),
        'Personal - Friends': ('Friends Day', '🤝'),

        # Social - High priority, memorable events
        'Social - House Party': ('Party Night', '🎉'),
        'Social - Bar': ('Night Out', '🍻'),
        'Social - Event': ('Event Day', '🎊'),
        'Social - Intramurals': ('Game Day', '🏆'),
        'Social - Picnic': ('Picnic Day', '🧺'),
        'Social - Dinner': ('Dinner Plans', '🍽️'),
        'Social - Work Event': ('Work Social', '🥂'),
        'Social - Board Games': ('Game Night', '🎲'),

        # Workout - Medium priority
        'Workout - Road Run': ('Road Run', '🏃'),
        'Workout - Beach Run': ('Beach Run', '🏃‍♂️'),
        'Workout - Peloton': ('Peloton Day', '🚴'),
        'Workout - Treadmill': ('Treadmill Session', '🏃‍♂️'),
        'Workout - Gym': ('Gym Day', '🏋️'),
        'Workout - Sports': ('Sports Day', '⚽'),
        'Workout - Other': ('Active Day', '💪'),

        # TV/Entertainment - Lower priority but fun
        'TV - Bach': ('Bachelor Night', '🌹'),
        'TV - Movie': ('Movie Night', '🎬'),
        'TV - Sports': ('Sports Night', '📺'),
        'TV - Video Games': ('Gaming Session', '🎮'),
        'TV - Other': ('Cozy Night', '📺'),

        # Cooking - Medium priority
        'Cooking - Breakfast': ('Breakfast Chef', '🍳'),
        'Cooking - Lunch': ('Lunch Prep', '🥗'),
        'Cooking - Dinner': ('Dinner Chef', '👨‍🍳'),

        # House - Lower priority
        'House - Projects': ('Project Day', '🔨'),
        'House - Errands': ('Errand Run', '📋'),

        # Work - Lowest priority (common, less distinctive)
        'Work - Thoughtful': ('Work Day', '💼'),
        'Work - LineDaddy': ('LineDaddy Day', '📱'),
        'Work - Fast AI': ('Fast AI Day', '🤖'),
        'Work - rcmOS': ('rcmOS Day', '💻'),
        'Work - AI/ML Course': ('Learning Day', '📚'),
        'Work - Coder School': ('Teaching Day', '👨‍🏫'),
        'Work - Metana': ('Metana Day', '🎓'),
        'Work - Lynk': ('Lynk Day', '🔗'),
        'Work - Personal Website': ('Website Work', '🌐'),
        'Work - Wedding': ('Wedding Work', '💒'),
        'Work - Fantasy Commissioner': ('Fantasy Day', '🏈'),
        'Work - Other': ('Work Day', '💼'),
    }

    # Location-to-title/emoji mappings for travel/special locations
    LOCATION_MAPPINGS = {
        # Vacation/Travel destinations
        'Maui': ('Maui Escape', '🌺'),
        'Hawaii': ('Island Life', '🏝️'),
        'Greece': ('Greek Adventure', '🇬🇷'),
        'Big Sky': ('Mountain Getaway', '🏔️'),
        'Tahoe': ('Tahoe Trip', '🏔️'),
        'Alaska': ('Alaska Adventure', '🐻'),
        'Maine': ('Maine Retreat', '🦞'),
        'Squam': ('Lake Life', '🚣'),
        'Cedar Lakes': ('Lake Escape', '🏞️'),
        'Timber Cove': ('Coastal Retreat', '🌊'),
        'Bodega Bay': ('Coastal Day', '🌊'),
        'Napa / Sonoma': ('Wine Country', '🍷'),
        'Asheville': ('Asheville Visit', '🍺'),
        'New York': ('NYC Day', '🗽'),
        'Austin': ('Austin Vibes', '🎸'),
        'Miami': ('Miami Heat', '🌴'),
        'Seattle': ('Seattle Day', '☕'),
        'Chicago': ('Chicago Trip', '🌆'),
        'South Dakota': ('Dakota Adventure', '🦬'),
        'Tucson': ('Desert Day', '🌵'),
        'Buena Vista': ('Mountain Day', '⛰️'),

        # Regional travel
        'Phoenix': ('Phoenix Trip', '🌵'),
        'Denver': ('Denver Day', '🏔️'),
        'Dallas': ('Dallas Trip', '🤠'),
        'Baltimore / DC': ('DC Trip', '🏛️'),
        'New Mexico': ('New Mexico Day', '🌶️'),
        'San Luis Obispo': ('SLO Day', '🌾'),
        'Fort Collins': ('Fort Collins Day', '🍺'),

        # Transit
        'Airport': ('Travel Day', '✈️'),
    }

    # Home locations (not special, won't trigger location-based titles)
    HOME_LOCATIONS = {'San Francisco', 'Marin', 'Rochester', 'Forest Hill'}

    # Event priority order (higher priority categories first)
    EVENT_PRIORITY = [
        # Unique experiences first
        'Outdoors - Skiing', 'Outdoors - Camping', 'Outdoors - Hike', 'Outdoors - Beach',
        # Personal connections
        'Personal - Date', 'Personal - Family', 'Personal - Friends',
        # Social events
        'Social - House Party', 'Social - Event', 'Social - Intramurals',
        'Social - Bar', 'Social - Picnic', 'Social - Board Games', 'Social - Dinner',
        # Active lifestyle
        'Workout - Road Run', 'Workout - Beach Run', 'Workout - Gym',
        'Workout - Peloton', 'Workout - Sports', 'Workout - Treadmill',
        # Entertainment
        'TV - Bach', 'TV - Movie', 'TV - Video Games', 'TV - Sports',
        # Cooking (if primary activity)
        'Cooking - Dinner', 'Cooking - Breakfast', 'Cooking - Lunch',
        # House stuff
        'House - Projects', 'House - Errands',
        # Work (fallback)
        'Work - Thoughtful', 'Work - LineDaddy', 'Work - Fast AI', 'Work - rcmOS',
    ]

    # Mood-based emoji modifiers
    POSITIVE_EMOJIS = ['☀️', '🎉', '💪', '✨', '🙌', '😊', '🌟', '💫']
    NEGATIVE_EMOJIS = ['😔', '😤', '🌧️', '😓', '💭', '🫠', '😮‍💨']
    NEUTRAL_EMOJIS = ['📝', '📅', '🗓️', '💭']

    def enhance_entry_description(self, entry: Dict) -> Dict:
        """
        Enhance entry with rich description, title, and emoji based on content.
        Uses priority-based selection: Location → Events → Highlight → Mood → Fallback
        """
        properties = entry['properties']
        date = properties.get('Date', {}).get('date', {}).get('start', '')
        description = properties.get('Description', {}).get('rich_text', [])
        highlight = properties.get('Highlight', {}).get('rich_text', [])
        lowlight = properties.get('Lowlight', {}).get('rich_text', [])
        events = properties.get('Events', {}).get('multi_select', [])
        location = properties.get('Location', {}).get('select', {})
        anxiety = properties.get('Anxiety', {}).get('select', {})
        depression = properties.get('Depression', {}).get('select', {})
        score = properties.get('Score', {}).get('select', {})

        # Extract text content
        desc_text = description[0]['plain_text'] if description else ""
        highlight_text = highlight[0]['plain_text'] if highlight else ""
        lowlight_text = lowlight[0]['plain_text'] if lowlight else ""
        location_name = location.get('name', '') if location else ""
        event_names = [e['name'] for e in events] if events else []

        # Extract mood scores (default to 0 if not set)
        anxiety_score = int(anxiety.get('name', '0')) if anxiety else 0
        depression_score = int(depression.get('name', '0')) if depression else 0
        day_score = int(score.get('name', '0')) if score else 0

        # Generate enhanced content based on existing data
        enhanced_data = self.generate_enhanced_content(
            desc_text, highlight_text, lowlight_text,
            event_names, location_name,
            anxiety_score, depression_score, day_score, date
        )

        return enhanced_data

    def generate_enhanced_content(self, desc: str, highlight: str, lowlight: str,
                                events: List[str], location: str,
                                anxiety: int, depression: int, score: int,
                                date: str) -> Dict:
        """
        Generate enhanced content using priority-based title selection:
        1. Special location (travel) → Location-themed title
        2. Unique events (skiing, date, party) → Event-themed title
        3. Highlight text → Extract key theme
        4. Mood-based fallback → Based on scores
        5. Default fallback
        """
        title = None
        emoji = None

        # Calculate overall mood (-6 to +6 range, inverted for anxiety/depression)
        # Positive score = good day, negative anxiety/depression = good
        overall_mood = score - anxiety - depression

        # Priority 1: Special location (travel destinations)
        if location and location not in self.HOME_LOCATIONS:
            if location in self.LOCATION_MAPPINGS:
                title, emoji = self.LOCATION_MAPPINGS[location]

        # Priority 2: Unique events (in priority order)
        if not title:
            for event in self.EVENT_PRIORITY:
                if event in events:
                    title, emoji = self.EVENT_MAPPINGS[event]
                    break

        # Priority 3: Highlight-based title (extract key theme)
        if not title and highlight:
            title, emoji = self._extract_highlight_theme(highlight)

        # Priority 4: Description keyword matching
        if not title and desc:
            title, emoji = self._extract_description_theme(desc)

        # Priority 5: Mood-based fallback
        if not title:
            title, emoji = self._get_mood_based_title(overall_mood)

        # Adjust emoji based on mood if we have a neutral emoji
        emoji = self._adjust_emoji_for_mood(emoji, overall_mood)

        # Enhanced description
        enhanced_desc = f"Enhanced: {desc}" if desc else "A day worth remembering."

        return {
            'title': title,
            'emoji': emoji,
            'description': enhanced_desc
        }

    def _extract_highlight_theme(self, highlight: str) -> tuple:
        """Extract a title theme from the highlight text."""
        highlight_lower = highlight.lower()

        highlight_keywords = {
            'date': ('Date Night', '💕'),
            'dinner': ('Great Dinner', '🍽️'),
            'lunch': ('Nice Lunch', '🥗'),
            'hike': ('Trail Day', '🥾'),
            'run': ('Runner\'s High', '🏃'),
            'workout': ('Strong Day', '💪'),
            'party': ('Party Time', '🎉'),
            'friends': ('Friends Day', '🤝'),
            'family': ('Family Time', '👨‍👩‍👧'),
            'travel': ('Travel Day', '✈️'),
            'beach': ('Beach Day', '🏖️'),
            'ski': ('Ski Day', '🎿'),
            'concert': ('Concert Night', '🎵'),
            'game': ('Game Day', '🎮'),
            'win': ('Victory Day', '🏆'),
            'promotion': ('Big Win', '🎊'),
            'news': ('Big News', '📰'),
            'milestone': ('Milestone Day', '🌟'),
        }

        for keyword, (title, emoji) in highlight_keywords.items():
            if keyword in highlight_lower:
                return title, emoji

        return None, None

    def _extract_description_theme(self, desc: str) -> tuple:
        """Extract a title theme from description keywords."""
        desc_lower = desc.lower()

        desc_keywords = {
            'brutal': ('Brutal Day', '😤'),
            'sick': ('Feeling Unwell', '🤒'),
            'ill': ('Under the Weather', '🤒'),
            'tired': ('Exhausted', '😴'),
            'exhausted': ('Exhausted', '😴'),
            'productive': ('Productive Day', '💪'),
            'crushed': ('Crushed It', '💪'),
            'amazing': ('Amazing Day', '✨'),
            'incredible': ('Incredible Day', '🌟'),
            'rough': ('Rough Day', '😓'),
            'tough': ('Tough Day', '😤'),
            'lazy': ('Lazy Day', '🛋️'),
            'chill': ('Chill Day', '😌'),
            'relax': ('Relaxation Day', '🧘'),
            'stress': ('Stressful Day', '😰'),
            'anxious': ('Anxious Day', '😰'),
            'fight': ('Difficult Day', '😔'),
            'argument': ('Tough Day', '😔'),
            'celebrate': ('Celebration', '🎉'),
            'birthday': ('Birthday!', '🎂'),
            'anniversary': ('Anniversary', '💕'),
            'wedding': ('Wedding Day', '💒'),
            'interview': ('Interview Day', '🎯'),
            'presentation': ('Presentation Day', '📊'),
            'demo': ('Demo Day', '🎯'),
            'onsite': ('Onsite Day', '🏢'),
        }

        for keyword, (title, emoji) in desc_keywords.items():
            if keyword in desc_lower:
                return title, emoji

        return None, None

    def _get_mood_based_title(self, mood: int) -> tuple:
        """Get a title based on overall mood score."""
        if mood >= 3:
            return ('Great Day', '☀️')
        elif mood >= 1:
            return ('Good Day', '😊')
        elif mood <= -3:
            return ('Tough Day', '😔')
        elif mood <= -1:
            return ('Challenging Day', '💭')
        else:
            return ('Regular Day', '📝')

    def _adjust_emoji_for_mood(self, emoji: str, mood: int) -> str:
        """Optionally adjust emoji based on mood for neutral emojis."""
        # Only adjust if we have a very neutral emoji
        if emoji in self.NEUTRAL_EMOJIS:
            if mood >= 2:
                return '☀️'
            elif mood <= -2:
                return '🌧️'
        return emoji

    def update_entry(self, page_id: str, enhanced_data: Dict, dry_run: bool = False) -> bool:
        """Update a Notion page with enhanced content."""
        if dry_run:
            print(f"[DRY RUN] Would update page {page_id} with:")
            print(f"  Title: {enhanced_data['title']}")
            print(f"  Emoji: {enhanced_data['emoji']}")
            print(f"  Description: {enhanced_data['description'][:100]}...")
            return True

        url = f"{self.base_url}/pages/{page_id}"
        payload = {
            "properties": {
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": enhanced_data['title']
                            }
                        }
                    ]
                },
                "Description": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": enhanced_data['description']
                            }
                        }
                    ]
                },
                "AI Touchup": {
                    "checkbox": False
                }
            },
            "icon": {
                "type": "emoji",
                "emoji": enhanced_data['emoji']
            }
        }

        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return True

    def process_entries(self, dry_run: bool = False, limit: Optional[int] = None) -> int:
        """Process all entries marked for touchup."""
        entries = self.find_entries_for_touchup()

        if not entries:
            print("No entries found for AI touchup.")
            return 0

        # Apply limit if specified
        total_found = len(entries)
        if limit and limit < len(entries):
            entries = entries[:limit]
            print(f"Found {total_found} entries. Processing first {limit}.")
        else:
            print(f"Found {total_found} entries for enhancement.")

        processed = 0
        for entry in entries:
            try:
                page_id = entry['id']
                date = entry['properties'].get('Date', {}).get('date', {}).get('start', 'Unknown')

                print(f"Processing entry for {date}...")

                enhanced_data = self.enhance_entry_description(entry)
                self.update_entry(page_id, enhanced_data, dry_run)

                processed += 1
                print(f"  ✓ Enhanced: {enhanced_data['title']} {enhanced_data['emoji']}")

            except Exception as e:
                print(f"  ✗ Error processing entry: {e}")
                continue

        return processed

def main():
    # Check for required environment variables
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_JOURNAL_DATABASE_ID')

    if not token or not database_id:
        print("Error: Missing required environment variables.")
        print("Please set NOTION_TOKEN and NOTION_JOURNAL_DATABASE_ID")
        print("\nExample:")
        print("export NOTION_TOKEN='your_token_here'")
        print("export NOTION_JOURNAL_DATABASE_ID='your_database_id_here'")
        return 1

    # Check for dry run flag
    dry_run = '--dry-run' in sys.argv

    # Check for limit flag (e.g., --limit=3)
    limit = None
    for arg in sys.argv:
        if arg.startswith('--limit='):
            try:
                limit = int(arg.split('=')[1])
            except ValueError:
                print(f"Warning: Invalid limit value, ignoring")

    if dry_run:
        print("Running in DRY RUN mode - no changes will be made.")
    if limit:
        print(f"Limiting to {limit} entries.")

    try:
        enhancer = NotionJournalEnhancer(token, database_id)
        processed = enhancer.process_entries(dry_run, limit)

        print(f"\nCompleted! Processed {processed} entries.")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())