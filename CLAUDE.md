# CLAUDE.md

Project guidance for Claude Code.

## Overview

Personal productivity tools built around Notion databases. Designed for expansion to multiple data workflows.

## Skills

Skills live in `.claude/skills/` and auto-trigger based on context:

- **journal-enhancing** - Enhance daily journal entries with AI-generated titles, emojis, and descriptions

## Environment

Environment variables load automatically via SessionStart hook:
- `NOTION_TOKEN` - Notion integration token
- `NOTION_JOURNAL_DATABASE_ID` - Journal database ID

Set these in `.env` (never commit).

## Notion API

- Bearer token authentication
- Notion-Version: 2022-06-28 header
- Filter entries using property queries
- Update pages with PATCH requests

## Security

- Never commit API tokens or secrets
- Use environment variables for configuration
- Be mindful of personal content in logs

## Future Skills

This project supports additional Notion-based skills:
- Habit tracking
- Reading list management
- Goal tracking
- Other personal data workflows
