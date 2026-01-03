# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal journal enhancement system built around a Notion database. The project enables automated enhancement of daily journal entries using AI to expand brief notes into rich, detailed narratives while maintaining the user's authentic voice.

## Architecture

### Core Components

1. **Notion Journal Database**: Contains daily entries with structured fields
   - Date, Name, Description, Location, Events, Scores, Highlight/Lowlight
   - "AI Touchup" checkbox to flag entries for enhancement

2. **Enhancement Script** (`scripts/notion_journal_enhancer.py`):
   - Connects to Notion API using integration token
   - Finds entries marked for AI touchup
   - Enhances descriptions with contextual narratives
   - Adds titles and emojis
   - Maintains user's writing style and voice

3. **Analysis Tools** (`scripts/analyze_dates.py`):
   - Identifies gaps in journal entries
   - Helps maintain consistency in daily logging

## Development Commands

### Setup
```bash
# Set environment variables (never commit these)
export NOTION_TOKEN="your_token"
export NOTION_DATABASE_ID="your_db_id"
```

### Enhancement
```bash
# Preview changes without applying
python3 scripts/notion_journal_enhancer.py --dry-run

# Apply enhancements
python3 scripts/notion_journal_enhancer.py
```

### Analysis
```bash
# Find missing journal dates
python3 scripts/analyze_dates.py
```

## Writing Style Guidelines

When enhancing journal entries, maintain these characteristics:
- **Personal and conversational tone**: "had a brutal day", "Maggie and I got into a fight"
- **Specific context**: Reference recurring people (Maggie, Winnie), work (Thoughtful, RFPs), activities
- **Emotional honesty**: Don't sanitize difficult feelings or conflicts
- **Natural flow**: Connect activities and emotions logically
- **Avoid generic language**: Use specific details over vague descriptions

## API Integration Patterns

### Notion API Usage
- Use bearer token authentication
- Notion-Version: 2022-06-28 header required
- Filter entries using property queries
- Update pages with PATCH requests
- Always uncheck "AI Touchup" flag after processing

### Entry Enhancement Process
1. Query for entries with AI Touchup = true
2. Extract existing content (description, highlight, lowlight, events)
3. Generate enhanced description maintaining user's voice
4. Add appropriate title (avoid day names like "Monday")
5. Select relevant emoji
6. Update entry and uncheck touchup flag

### Title & Emoji Generation System

The enhancer uses a **priority-based selection system** with default mappings that serve as **suggestions for Claude to improve upon at inference time**. The static mappings provide a baseline, but Claude is expected to apply creativity to generate more varied, contextually-appropriate titles and emojis.

#### Design Philosophy
- **Mappings are starting points, not final answers** - The hardcoded mappings ensure basic functionality, but Claude should use context from the full entry (description, highlight, lowlight, mood) to craft better titles
- **Avoid repetitive titles** - "Regular Day" and generic titles should be rare; Claude should find something distinctive about each day
- **Emojis should reflect tone** - Match the emotional tenor of the entry, not just the activity
- **Descriptions should be rich narratives** - The "Enhanced: {desc}" template is a placeholder; Claude should expand brief notes into full paragraphs

#### Priority Order for Title Selection (highest to lowest):

1. **Special Location** - Travel destinations trigger location-themed titles
   - Example: Maui → "Maui Escape 🌺", NYC → "NYC Day 🗽"
   - Home locations (San Francisco, Marin, Rochester, Forest Hill) are excluded
   - *Claude should craft location-specific titles that capture the trip's vibe*

2. **Unique Events** - Events checked in priority order:
   - Outdoors first: Skiing 🎿, Camping 🏕️, Hiking 🥾, Beach 🏖️
   - Personal connections: Date 💕, Family 👨‍👩‍👧, Friends 🤝
   - Social events: House Party 🎉, Bar 🍻, Intramurals 🏆
   - Workouts: Road Run 🏃, Gym 🏋️, Peloton 🚴
   - Entertainment: Bachelor 🌹, Movie 🎬, Video Games 🎮
   - Cooking: Dinner 👨‍🍳, Breakfast 🍳
   - Work (lowest priority): Thoughtful 💼, LineDaddy 📱, etc.
   - *Claude should combine multiple events creatively when relevant*

3. **Highlight Text** - Extract themes from the highlight field
   - *Claude should use the highlight to inspire a unique title, not just match keywords*

4. **Description Keywords** - Emotional/activity keywords as fallback
   - "brutal", "productive", "crushed", "birthday", "onsite", etc.
   - *Claude should read the full description for context, not just keyword-match*

5. **Mood-Based Fallback** - Uses combined mood score:
   - Score ≥ 3: "Great Day ☀️"
   - Score ≥ 1: "Good Day 😊"
   - Score ≤ -3: "Tough Day 😔"
   - Score ≤ -1: "Challenging Day 💭"
   - *Claude should find something more distinctive when possible*

#### Mood Score Calculation
```
overall_mood = Score - Anxiety - Depression
```
- Range: -6 to +6
- High Score = good day, Low Anxiety/Depression = good
- Neutral emojis (📝, 📅) can be upgraded to ☀️ or 🌧️ based on mood

#### Database Fields Available for Context

| Field | Type | Usage |
|-------|------|-------|
| `Location` | select | Travel detection, 32 locations available |
| `Events` | multi_select | Activity categorization, 47 event types |
| `Highlight` | rich_text | Best moment of the day |
| `Lowlight` | rich_text | Challenge or difficulty |
| `Description` | rich_text | Raw notes about the day |
| `Score` | select (-2 to +2) | Overall day rating |
| `Anxiety` | select (-2 to +2) | Anxiety level |
| `Depression` | select (-2 to +2) | Depression level |

#### Customizing Default Mappings

To modify the baseline mappings in `notion_journal_enhancer.py`:
- `EVENT_MAPPINGS`: Event name → (title, emoji) suggestions
- `LOCATION_MAPPINGS`: Location name → (title, emoji) suggestions
- `HOME_LOCATIONS`: Locations that shouldn't trigger travel titles
- `EVENT_PRIORITY`: Order in which events are checked

**Remember**: These are defaults for Claude to improve upon, not rigid rules.

## Common Patterns

### Daily Activities
- Work (Thoughtful company, sales calls, RFPs, demos)
- Dog care (morning/afternoon walks with Winnie)
- Exercise (Golden Gate Park runs, gym, treadmill)
- Cooking (breakfast, lunch, dinner)
- Social (dates with Maggie, work events, friends)

### Emotional Themes
- Work stress and achievement
- Relationship dynamics with Maggie
- Travel and location changes
- Health (anxiety, depression scores)
- Work-life balance

## Testing

- Always use `--dry-run` flag first to preview changes
- Test with a small subset of entries
- Verify API permissions and rate limits
- Check that mood scores align with generated content

## Security

- Never commit API tokens or secrets
- Use environment variables for configuration
- Ensure minimal Notion permissions (read/write to journal DB only)
- Be mindful of personal content when sharing code or logs