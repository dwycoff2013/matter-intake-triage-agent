"""Deterministic safety guardrails for LexTriage local flows.

These helpers are deliberately local and regex-based so tests and demos can run
without live model calls. They enforce the same boundaries described in the docs:
common identifier redaction, legal-advice and prompt-injection detection,
human-review routing, and final packet PII checks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from app.tools.redaction import redact_pii

LEGAL_ADVICE_RE = re.compile(
    r"\b(exactly what I should|guarantee|should I ignore|legal strategy)\b", re.I
)
PROMPT_INJECTION_RE = re.compile(
    r"\b(ignore previous instructions|system override|disregard all guardrails)\b", re.I
)
COMMON_PII_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    re.compile(r"\b\d{3}[-\s]\d{2}[-\s]\d{4}\b"),
    re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{1,7}\b"),
)
SENSITIVE_MATTER_AREAS = {
    "Criminal Defense",
    "Immigration Defense",
    "Family / Domestic Law",
    "Civil Rights",
}
RISK_URGENCIES = {"critical", "high"}


@dataclass(frozen=True)
class GuardrailResult:
    """Deterministic safety assessment for one intake."""

    redacted_text: str
    redaction_count: int
    legal_advice_requested: bool
    prompt_injection_detected: bool
    human_review_required: bool
    compliance_flags: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "redacted_text": self.redacted_text,
            "redaction_count": self.redaction_count,
            "legal_advice_requested": self.legal_advice_requested,
            "prompt_injection_detected": self.prompt_injection_detected,
            "human_review_required": self.human_review_required,
            "compliance_flags": list(self.compliance_flags),
        }


def predict_urgency(deadline_date: str, *, today: date) -> str:
    """Classify urgency relative to an explicit clock date."""
    if not deadline_date:
        return "none"
    days = (date.fromisoformat(deadline_date) - today).days
    if days <= 3:
        return "critical"
    if days <= 10:
        return "high"
    if days <= 30:
        return "medium"
    return "routine"


def common_pii_found(text: str) -> bool:
    """Return True if text contains currently supported common PII patterns."""
    return any(pattern.search(str(text or "")) for pattern in COMMON_PII_PATTERNS)


def assess_intake(
    text: str,
    *,
    urgency: str = "none",
    matter_area: str = "",
    needs_human_review: bool = False,
) -> GuardrailResult:
    """Run deterministic safety guardrails over raw intake text."""
    redaction = redact_pii(text)
    legal_advice = bool(LEGAL_ADVICE_RE.search(text or ""))
    prompt_injection = bool(PROMPT_INJECTION_RE.search(text or ""))
    normalized_urgency = str(urgency or "none").lower()
    human_review = bool(
        needs_human_review
        or legal_advice
        or prompt_injection
        or normalized_urgency in RISK_URGENCIES
        or matter_area in SENSITIVE_MATTER_AREAS
    )
    flags: list[str] = []
    if redaction["redaction_count"]:
        flags.append("common_pii_redacted")
    if legal_advice:
        flags.append("legal_advice_request")
    if prompt_injection:
        flags.append("prompt_injection")
    if normalized_urgency in RISK_URGENCIES:
        flags.append("urgent_deadline")
    if matter_area in SENSITIVE_MATTER_AREAS:
        flags.append("sensitive_matter_area")
    if human_review:
        flags.append("human_review_required")
    return GuardrailResult(
        redacted_text=str(redaction["redacted_text"]),
        redaction_count=int(redaction["redaction_count"]),
        legal_advice_requested=legal_advice,
        prompt_injection_detected=prompt_injection,
        human_review_required=human_review,
        compliance_flags=tuple(flags),
    )


def validate_final_packet(packet_text: str) -> tuple[bool, list[str]]:
    """Validate final packet text against implemented deterministic guardrails."""
    errors: list[str] = []
    if common_pii_found(packet_text):
        errors.append("packet contains supported common PII pattern")
    if "legal advice" not in str(packet_text or "").lower():
        errors.append("packet should include a legal-advice limitation/disclaimer")
    return not errors, errors
