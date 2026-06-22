"""Date extraction and calculation tools.

MCP-style local tool layer for deadline triage operations.
"""

import re
from datetime import datetime, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Supported date formats for parsing
# ---------------------------------------------------------------------------
_DATE_FORMATS = [
    "%Y-%m-%d",       # 2024-03-05
    "%m/%d/%Y",       # 03/05/2024
    "%m-%d-%Y",       # 03-05-2024
    "%m.%d.%Y",       # 03.05.2024
    "%B %d, %Y",      # March 5, 2024
    "%b %d, %Y",      # Mar 5, 2024
    "%B %d %Y",       # March 5 2024
    "%b %d %Y",       # Mar 5 2024
    "%d %B %Y",       # 5 March 2024
    "%d %b %Y",       # 5 Mar 2024
]


def _try_parse_date(date_str: str) -> Optional[datetime]:
    """Attempt to parse a date string against all known formats."""
    cleaned = date_str.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def _count_business_days(start: datetime, end: datetime) -> int:
    """Count weekday-only days between two dates (exclusive of start)."""
    if start > end:
        start, end = end, start
    count = 0
    current = start + timedelta(days=1)
    while current <= end:
        if current.weekday() < 5:  # Mon-Fri
            count += 1
        current += timedelta(days=1)
    return count


# ===== ADK Tool Functions =====


def calculate_days_between_dates(start_date: str, end_date: str) -> dict:
    """Calculate the number of calendar and business days between two dates.

    Accepts ISO-8601 (YYYY-MM-DD), US (MM/DD/YYYY), and written
    (Month DD, YYYY) formats.

    Args:
        start_date: The starting date string.
        end_date: The ending date string.

    Returns:
        dict with status, date info, calendar days, and business days.
    """
    d1 = _try_parse_date(start_date)
    if d1 is None:
        return {
            "status": "error",
            "message": f"Could not parse start_date: '{start_date}'. "
                       f"Supported formats: YYYY-MM-DD, MM/DD/YYYY, Month DD YYYY.",
        }

    d2 = _try_parse_date(end_date)
    if d2 is None:
        return {
            "status": "error",
            "message": f"Could not parse end_date: '{end_date}'. "
                       f"Supported formats: YYYY-MM-DD, MM/DD/YYYY, Month DD YYYY.",
        }

    calendar_days = abs((d2 - d1).days)
    business_days = _count_business_days(min(d1, d2), max(d1, d2))

    return {
        "status": "success",
        "start_date": d1.strftime("%Y-%m-%d"),
        "end_date": d2.strftime("%Y-%m-%d"),
        "days_between": calendar_days,
        "calendar_days": calendar_days,
        "business_days": business_days,
    }


def extract_dates_regex(text: str) -> dict:
    """Scan text for date patterns and return normalized results.

    Detects dates in the following formats:
    - ISO: YYYY-MM-DD
    - US numeric: MM/DD/YYYY, MM-DD-YYYY, MM.DD.YYYY
    - Written: January 5, 2024 / Jan 5, 2024 / 5 January 2024

    Args:
        text: The text to scan for dates.

    Returns:
        dict with status, list of found dates (raw, normalized, position),
        and total count.
    """
    patterns = [
        # ISO: 2024-03-05
        (r'\b(\d{4}-\d{1,2}-\d{1,2})\b', None),
        # US numeric: 03/05/2024, 03-05-2024, 03.05.2024
        (r'\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})\b', None),
        # Written long: March 5, 2024 / March 5 2024
        (r'\b((?:January|February|March|April|May|June|July|August|September|'
         r'October|November|December)\s+\d{1,2},?\s+\d{4})\b', None),
        # Written short: Mar 5, 2024 / Mar 5 2024
        (r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
         r'\s+\d{1,2},?\s+\d{4})\b', None),
        # Day-first written: 5 March 2024
        (r'\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|'
         r'September|October|November|December)\s+\d{4})\b', None),
    ]

    found: list[dict] = []
    seen_positions: set[int] = set()

    for pattern, _ in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            pos = match.start()
            # Avoid duplicate matches at the same position
            if pos in seen_positions:
                continue
            seen_positions.add(pos)

            raw = match.group(1)
            parsed = _try_parse_date(raw)
            normalized = parsed.strftime("%Y-%m-%d") if parsed else raw

            found.append({
                "raw": raw,
                "normalized": normalized,
                "position": pos,
            })

    # Sort by position in the original text
    found.sort(key=lambda d: d["position"])

    return {
        "status": "success",
        "dates_found": found,
        "count": len(found),
    }
