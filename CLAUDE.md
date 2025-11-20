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