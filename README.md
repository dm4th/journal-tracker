# Personal Journal Enhancement System

This repository contains tools for enhancing and managing a personal journal stored in Notion.

## Overview

The journal system uses a Notion database to track daily entries with the following structure:

- **Date**: The date of the entry
- **Name**: A descriptive title for the day
- **Description**: Detailed narrative of the day
- **Location**: Where the day took place
- **Events**: Multi-select tags for activities (Work, Dog Walks, Workouts, etc.)
- **Score**: Overall day rating (-2 to +2)
- **Anxiety**: Anxiety level (-2 to +2)
- **Depression**: Depression level (-2 to +2)
- **Highlight**: Best part of the day
- **Lowlight**: Worst part of the day
- **AI Touchup**: Checkbox to mark entries for enhancement

## Features

### Automated Journal Enhancement

The system can automatically enhance journal entries by:

- Finding entries marked with the "AI Touchup" checkbox
- Expanding brief notes into rich, detailed descriptions
- Adding descriptive titles that capture the essence of the day
- Adding relevant emojis to make entries more engaging
- Maintaining the user's authentic writing voice and style
- Unchecking the touchup flag when complete

### Writing Style

Enhanced entries follow these patterns:
- Conversational and personal tone
- Contextual details about relationships (Maggie, Winnie the dog)
- Work-life balance themes
- Emotional honesty about difficult days
- Specific details about activities and feelings

## Usage

### Prerequisites

1. Notion integration token with access to your journal database
2. Database ID of your journal
3. Python 3.6+ with requests library

### Setup Environment Variables

```bash
export NOTION_TOKEN="your_notion_integration_token"
export NOTION_DATABASE_ID="your_database_id"
```

### Run the Enhancer

```bash
# Dry run (preview changes without applying)
python3 scripts/notion_journal_enhancer.py --dry-run

# Actually enhance entries
python3 scripts/notion_journal_enhancer.py
```

### Date Analysis

```bash
# Analyze gaps in journal entries
python3 scripts/analyze_dates.py
```

## Journal Entry Examples

### Before Enhancement
```
Description: "Early wake up. Endless RFP'S. 13 hour Work day. Fight with Maggie over dinner"
```

### After Enhancement
```
Title: "Brutal Day" 😤
Description: "Absolutely brutal day. Up early and immediately slammed with endless RFPs - the pipeline is insane right now. Worked a grueling 13-hour day trying to keep up with everything. Had one good sales pitch which felt like a small win in the chaos. Evening took a bad turn when Maggie and I got into a fight over dinner about her feeling like my family doesn't love her. Really tough conversation that left us both upset. Just an exhausting day all around."
```

## Project Structure

```
journal/
├── scripts/
│   ├── notion_journal_enhancer.py  # Main enhancement script
│   └── analyze_dates.py            # Date gap analysis
├── README.md                       # This file
└── CLAUDE.md                       # Claude Code guidance
```

## Development Notes

This system was developed using Claude Code (claude.ai/code) to:
- Connect to the Notion API
- Analyze existing journal patterns
- Generate authentic enhancements
- Maintain consistency with the user's voice

The enhancement process preserves the emotional authenticity and personal details that make journal entries meaningful for future reflection.

## Security

- Never commit API tokens to the repository
- Use environment variables for sensitive configuration
- Ensure Notion integration has minimal required permissions