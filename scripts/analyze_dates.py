#!/usr/bin/env python3
from datetime import datetime, timedelta
import json

# Recent journal dates from the API response
journal_dates = [
    "2025-11-09", "2025-11-08", "2025-11-07", "2025-11-06", "2025-10-29",
    "2025-10-28", "2025-10-27", "2025-10-25", "2025-10-24", "2025-10-23", "2025-10-22"
]

# Convert to datetime objects and sort
dates = [datetime.strptime(date, "%Y-%m-%d") for date in journal_dates]
dates.sort(reverse=True)

# Find missing dates between earliest and latest
start_date = dates[-1]
end_date = dates[0]

all_dates = []
current_date = start_date
while current_date <= end_date:
    all_dates.append(current_date.strftime("%Y-%m-%d"))
    current_date += timedelta(days=1)

missing_dates = [date for date in all_dates if date not in journal_dates]

print("Missing journal dates:")
for date in missing_dates:
    print(f"  - {date}")

print(f"\nTotal missing: {len(missing_dates)} days")