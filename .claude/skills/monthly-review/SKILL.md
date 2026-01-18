---
name: monthly-review
description: Generate monthly progress reports against 2026 goals. Analyze journal entries, track goal progress, identify patterns, and provide recommendations.
allowed-tools: Read, Bash(python3:*), Bash(export:*)
---

# Monthly Review Skill

Generate comprehensive monthly check-ins to track progress against your 2026 goals. Analyzes journal data, calculates goal achievement, and provides actionable insights.

## Quick Start

```bash
# Analyze previous month (default)
export $(grep -v '^#' .env | xargs) && python3 .claude/skills/monthly-review/scripts/monthly_analyze.py

# Analyze specific month
export $(grep -v '^#' .env | xargs) && python3 .claude/skills/monthly-review/scripts/monthly_analyze.py --month=2026-01

# Full year analysis
export $(grep -v '^#' .env | xargs) && python3 .claude/skills/monthly-review/scripts/monthly_analyze.py --year=2026
```

## 2026 Goals Reference

Based on 2025 Year in Review findings, these are the tracked goals:

### Physical Fitness
| Goal | Monthly Target | Yearly Target | 2025 Performance |
|------|---------------|---------------|------------------|
| Gym Sessions | 9 | 104 | 33 (32%) - needs improvement |
| Dog Walks | 28 | 336 | 339 (93%) - maintain |
| Road Runs | 4 | 48 | 29 (new explicit target) |

### Relationships
| Goal | Monthly Target | Yearly Target | 2025 Performance |
|------|---------------|---------------|------------------|
| Date Nights | 2 | 24 | 30 (125%) - exceeded |
| Social Events | 3 | 36 | 43 (119%) - exceeded |

### Consistency
| Goal | Monthly Target | Yearly Target | 2025 Performance |
|------|---------------|---------------|------------------|
| Journal Entries | 28 | 340 | 315 (86%) - maintain |

### Mental Health
| Goal | Monthly Target | 2025 Baseline |
|------|---------------|---------------|
| Positive Days | ≥35% | 34% |
| Limit Negative Days | <20% | 32% |

## Output Format

The analyzer outputs JSON with:

```json
{
  "month": "2026-01",
  "entry_count": 28,
  "score_stats": {
    "average": 0.15,
    "positive_days": 10,
    "negative_days": 6,
    "positive_pct": 35.7,
    "negative_pct": 21.4
  },
  "goal_progress": {
    "gym": {
      "name": "Gym Sessions",
      "count": 8,
      "target": 9,
      "percentage": 88.9,
      "status": "CLOSE"
    }
    // ... more goals
  },
  "events": { /* event counts */ },
  "locations": { /* location counts */ },
  "highlights": [ /* top moments */ ],
  "lowlights": [ /* challenges */ ],
  "qualitative": {
    "drinking": { "count": 2, "entries": [...] },
    "work_stress": { "count": 5, "entries": [...] }
  }
}
```

## Status Indicators

| Status | Meaning | Percentage |
|--------|---------|------------|
| ON_TRACK | Meeting or exceeding target | ≥100% |
| CLOSE | Nearly there | 75-99% |
| NEEDS_ATTENTION | Falling behind | 50-74% |
| OFF_TRACK | Significantly behind | <50% |

## Report Generation Workflow

### Step 1: Run Analysis
```bash
export $(grep -v '^#' .env | xargs) && python3 .claude/skills/monthly-review/scripts/monthly_analyze.py --month=2026-01
```

### Step 2: Generate Report

Using the JSON output, create a report with:

1. **Quick Summary**
   - Overall month score average
   - Days journaled / days in month
   - One-line goal status

2. **Goal Progress Table**
   - Each goal with count, target, status
   - Color-code by status

3. **Highlights Section**
   - Top 3-5 best moments
   - Common themes

4. **Challenges Section**
   - Key lowlights
   - Patterns to address

5. **Recommendations**
   - Action items for next month
   - Goals needing attention

## Qualitative Tracking

The analyzer searches for keywords to track goals that can't be measured by events:

- **Drinking**: beer, wine, alcohol, cocktail, etc.
- **Reading**: book, kindle, reading
- **Screens**: phone, doom scroll, instagram, etc.
- **Work Stress**: boundary, overwork, exhausted, meetings

## Configuration

Goals are defined in `goals-2026.json`. To update targets:

1. Edit `.claude/skills/monthly-review/goals-2026.json`
2. Update `target_monthly` or `target_yearly` values
3. Add new `event_patterns` to track additional activities

## Year-over-Year Comparison

To compare with 2025 baseline:
- Use the 2025 Year in Review report at `2025-year-in-review.md`
- Compare quarterly trends
- Identify improvements or regressions

## Tips

1. **Run monthly**: Set a calendar reminder for the 1st of each month
2. **Review trends**: Compare month-over-month to catch slipping habits early
3. **Adjust targets**: If consistently hitting 150%+, consider raising the bar
4. **Track qualitative**: Note when keyword searches reveal patterns

## Troubleshooting

**Missing data**: Ensure NOTION_TOKEN and NOTION_JOURNAL_DATABASE_ID are set in .env

**No entries**: Check if journal has entries for the requested month

**Wrong counts**: Verify event_patterns match your actual Notion multi-select values
