"""PII redaction tool.

MCP-style local tool layer for security & compliance operations.
"""

import re
from typing import NamedTuple


class _RedactionMatch(NamedTuple):
    type: str
    original: str
    start: int
    end: int


# ---------------------------------------------------------------------------
# PII regex patterns (ordered by specificity — most specific first)
# ---------------------------------------------------------------------------
_PII_PATTERNS: list[tuple[str, re.Pattern]] = [
    # SSN: 123-45-6789 or 123 45 6789
    ("SSN", re.compile(r'\b\d{3}[-\s]\d{2}[-\s]\d{4}\b')),

    # Credit card: 4111-1111-1111-1111 or 4111111111111111 (13-19 digits)
    ("CREDIT_CARD", re.compile(
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{1,7}\b'
    )),

    # Email
    ("EMAIL", re.compile(
        r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
    )),

    # Phone: (555) 123-4567, 555-123-4567, 555.123.4567, +1-555-123-4567
    ("PHONE", re.compile(
        r'(?:\+?1[-.\s]?)?'               # optional country code
        r'(?:\(\d{3}\)|\d{3})'             # area code
        r'[-.\s]?\d{3}[-.\s]?\d{4}\b'
    )),
]

# Placeholder template per PII type
_PLACEHOLDER = {
    "SSN": "[SSN REDACTED]",
    "CREDIT_CARD": "[PAYMENT REDACTED]",
    "EMAIL": "[EMAIL REDACTED]",
    "PHONE": "[PHONE REDACTED]",
}


# ===== ADK Tool Function =====


def redact_pii(text: str) -> dict:
    """Detect and redact personally identifiable information from text.

    Scans for SSN, phone numbers, email addresses, and credit card numbers.
    Each detected item is replaced with a typed placeholder
    (e.g. ``[SSN REDACTED]``).

    Args:
        text: The text to scan and redact.

    Returns:
        dict with redacted_text, list of redactions (type, original,
        position), and redaction_count.
    """
    matches: list[_RedactionMatch] = []

    for pii_type, pattern in _PII_PATTERNS:
        for m in pattern.finditer(text):
            # Avoid overlapping matches — skip if this span overlaps an
            # already-recorded match
            overlaps = any(
                not (m.end() <= existing.start or m.start() >= existing.end)
                for existing in matches
            )
            if overlaps:
                continue
            matches.append(
                _RedactionMatch(pii_type, m.group(), m.start(), m.end())
            )

    # Sort by position (descending) so replacements don't shift offsets
    matches.sort(key=lambda r: r.start, reverse=True)

    redacted = text
    redactions: list[dict] = []

    for match in matches:
        replacement_token = _PLACEHOLDER.get(match.type, "[REDACTED]")
        redacted = redacted[:match.start] + replacement_token + redacted[match.end:]
        redactions.append({
            "type": match.type,
            "original": match.original,
            "position": match.start,
        })

    # Return redactions in document order (ascending position)
    redactions.reverse()

    return {
        "status": "success",
        "redacted_text": redacted,
        "redactions": redactions,
        "redaction_count": len(redactions),
    }
