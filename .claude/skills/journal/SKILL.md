---
name: journal
description: Enhance personal journal entries from Notion. Read entries marked for AI touchup, craft creative titles, emojis, and rich narrative descriptions, then write them back. Also find gaps in journal entries.
allowed-tools: Read, Bash(python3:*)
---

# Journal Enhancement Skill

Enhance daily journal entries stored in a Notion database. Transform brief notes into rich, detailed narratives while maintaining Danny's authentic voice and emotional honesty.

## Workflow

### Step 1: Read Entries

```bash
python3 .claude/skills/journal/scripts/journal_read.py [--limit=N]
```

Returns JSON with entries containing:
- `page_id` - Notion page identifier
- `date` - Entry date
- `current_title` - Existing title
- `description` - Raw notes about the day
- `highlight` - Best moment of the day
- `lowlight` - Challenge or difficulty
- `location` - Where the day took place
- `events` - Activities that occurred (multi-select)
- `score`, `anxiety`, `depression` - Mood scores (-2 to +2)

### Step 2: Enhance Each Entry

For each entry, generate:
1. **Title** - Creative, evocative (never use day names like "Monday")
2. **Emoji** - Matches emotional tenor, not just activity
3. **Description** - Rich narrative expanding brief notes (keep it concise)

### Step 3: Write Enhanced Entries

```bash
python3 .claude/skills/journal/scripts/journal_write.py '<json_data>'
```

JSON format:
```json
{
  "page_id": "xxx-xxx-xxx",
  "title": "Creative Title Here",
  "emoji": "...",
  "description": "Enhanced narrative description..."
}
```

Supports single entry or array of entries.

### Finding Missing Dates

```bash
python3 .claude/skills/journal/scripts/journal_gaps.py [--days=N]
```

Queries Notion for all journal dates and reports gaps.

---

## Title & Emoji Priority System

Use this priority order (highest to lowest):

### 1. Special Location (Travel)
Travel destinations trigger location-themed titles. Home locations (San Francisco, Marin, Rochester, Forest Hill) are excluded.
- Maui: "Island Paradise", "Maui Magic"
- NYC: "City Adventures", "Manhattan Hustle"
- Greece: "Greek Odyssey", "Mediterranean Days"

### 2. Unique Events (in priority order)
- **Outdoors**: Skiing, Camping, Hiking, Beach
- **Personal**: Date, Family, Friends
- **Social**: House Party, Bar, Intramurals, Board Games
- **Workouts**: Road Run, Gym, Peloton, Beach Run
- **Entertainment**: Bachelor, Movie, Video Games
- **Cooking**: Dinner, Breakfast, Lunch
- **Work (lowest)**: Thoughtful, LineDaddy, etc.

Combine multiple events creatively when relevant!

### 3. Highlight Text
Use the highlight to inspire a unique title. If highlight mentions a win, achievement, or special moment, center the title around that.

### 4. Description Keywords
Emotional keywords: "brutal", "productive", "crushed", "amazing", "rough", "birthday", "onsite"

### 5. Mood-Based Fallback
Use overall mood calculation (see below) to inform tone when nothing else stands out.

**Key principle**: Find something distinctive about each day. Avoid generic titles like "Regular Day".

---

## Voice & Style Guidelines

### Tone
- **Personal and conversational**: "had a brutal day", "Maggie and I got into a fight"
- **Emotionally honest**: Don't sanitize difficult feelings or conflicts
- **Specific over generic**: Reference actual places, people, activities

### Recurring Context
- **People**: Maggie (wife), Winnie (dog)
- **Work**: Thoughtful (company), RFPs, sales calls, demos, onsites
- **Side projects**: LineDaddy, Fast AI, rcmOS
- **Exercise**: Golden Gate Park runs, gym sessions, Peloton, treadmill
- **Social**: Date nights, work events, intramural sports, friends

### Description Expansion

Transform brief notes into concise narratives:

**Input**: "brutal work day, long RFP, walked Winnie, made pasta"

**Output**: "Brutal work day grinding through a massive RFP. The afternoon walk with Winnie was a needed reset. Made fresh pasta for dinner - exactly the comfort I needed."

**Techniques**:
- Add emotional context to activities
- Connect events where appropriate
- Keep it concise - expand but don't over-elaborate
- Maintain first-person, authentic voice

---

## Mood Score System

### Score Field (50% weight) - Overall day rating
- +2: Exceptional day
- +1: Good day
- 0: Neutral
- -1: Below average
- -2: Rough day

### Anxiety Field (25% weight)
- +2: Relaxed, feeling great
- +1: Calm
- 0: Baseline
- -1: Somewhat anxious
- -2: Very anxious day

### Depression Field (25% weight)
- +2: Energized, upbeat
- +1: Good mood
- 0: Baseline
- -1: Low energy
- -2: Depressed/down

### Combined Mood Calculation
```
overall_mood = (Score * 0.5) + (Anxiety * 0.25) + (Depression * 0.25)
```
Range: -2 to +2

- Positive overall = upbeat narrative, sunny emojis
- Negative overall = acknowledge difficulty, empathetic tone

**Focus primarily on the Score field** - it's the most important indicator.

---

## Database Fields Reference

| Field | Type | Usage |
|-------|------|-------|
| `Location` | select | 32 locations (travel vs home detection) |
| `Events` | multi_select | 47 event types |
| `Highlight` | rich_text | Best moment |
| `Lowlight` | rich_text | Challenge/difficulty |
| `Description` | rich_text | Raw notes |
| `Score` | select (-2 to +2) | Day rating (primary) |
| `Anxiety` | select (-2 to +2) | Higher = better |
| `Depression` | select (-2 to +2) | Higher = better |

---

## Tips

1. **Preview first**: Use `--limit=1` to test one entry before batch processing
2. **Avoid repetition**: Each title should be unique within a batch
3. **Match emoji to emotion**: Not just activity - a rough gym day gets a different emoji than a triumphant one
4. **Read the lowlight**: It often reveals the true emotional tenor of the day
5. **Keep it tight**: Expand notes but don't over-elaborate
