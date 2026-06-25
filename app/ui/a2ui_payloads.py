"""A2UI-style structured intake payloads for human-review demos."""

from __future__ import annotations

SENSITIVE_AREAS = {"Criminal Defense", "Immigration Defense", "Family / Domestic Law", "Civil Rights"}
RISK_URGENCIES = {"high", "critical"}


def _case_id(case: dict) -> str:
    return str(case.get("case_id") or case.get("id") or "CASE-UNKNOWN")


def _urgency(case: dict) -> str:
    return str(case.get("predicted_urgency") or case.get("expected_urgency") or case.get("urgency") or "none").lower()


def _human_review_required(case: dict, eval_result: dict | None = None) -> bool:
    eval_result = eval_result or {}
    return bool(
        case.get("needs_human_review")
        or case.get("human_review_required")
        or eval_result.get("human_review_predicted")
        or case.get("asks_legal_advice")
        or case.get("prompt_injection")
        or _urgency(case) in RISK_URGENCIES
        or case.get("matter_area") in SENSITIVE_AREAS
    )


def build_a2ui_intake_payload(case: dict, eval_result: dict | None = None) -> dict:
    """Build a JSON-serializable A2UI-style payload for legal intake review."""

    eval_result = eval_result or {}
    urgency = _urgency(case)
    human_review = _human_review_required(case, eval_result)
    flags = [flag for flag, present in {
        "legal_advice_request": case.get("asks_legal_advice") or eval_result.get("legal_advice_detected"),
        "prompt_injection": case.get("prompt_injection") or eval_result.get("prompt_injection_detected"),
        "sensitive_matter_area": case.get("matter_area") in SENSITIVE_AREAS,
        "urgent_deadline": urgency in RISK_URGENCIES,
    }.items() if present]
    components: list[dict] = []
    if human_review or urgency in RISK_URGENCIES:
        components.append({
            "type": "risk_banner",
            "severity": "critical" if urgency == "critical" else "high" if urgency == "high" else "review",
            "message": "Human review required before legal advice or client-facing recommendations.",
        })
    components.extend([
        {
            "type": "matter_summary_card",
            "matter_area": case.get("matter_area", "Unknown"),
            "matter_subtype": case.get("matter_subtype", "Unknown"),
            "urgency": urgency,
            "summary": case.get("intake_text", "")[:280],
        },
        {
            "type": "deadline_timeline",
            "deadline_date": case.get("deadline_date") or None,
            "urgency": urgency,
            "uncertainty": not bool(case.get("deadline_date")),
        },
        {"type": "safety_flags", "flags": flags, "human_review_required": human_review},
        {
            "type": "missing_information_checklist",
            "items": [
                "Confirm conflict check details.",
                "Collect relevant notices, pleadings, contracts, or correspondence.",
                "Confirm deadline source and service date.",
            ],
        },
        {
            "type": "recommended_next_actions",
            "items": [
                "Route packet to supervising attorney or intake specialist.",
                "Request missing documents using the checklist.",
                "Avoid providing legal advice in automated responses.",
            ],
        },
    ])
    if human_review:
        components.append({
            "type": "human_review_disclaimer",
            "text": "This structured intake payload is a triage aid only and requires qualified human review.",
        })
    return {
        "schema": "lextriage.a2ui.v1",
        "case_id": _case_id(case),
        "title": "LexTriage Intake Review",
        "human_review_required": human_review,
        "components": components,
    }


def validate_a2ui_payload(payload: dict) -> tuple[bool, list[str]]:
    """Validate core A2UI-style payload invariants."""

    errors: list[str] = []
    if payload.get("schema") != "lextriage.a2ui.v1":
        errors.append("schema must be lextriage.a2ui.v1")
    if not payload.get("case_id"):
        errors.append("case_id is required")
    components = payload.get("components")
    if not isinstance(components, list) or not components:
        errors.append("components must be a non-empty list")
        components = []
    component_types = []
    for idx, component in enumerate(components):
        if not isinstance(component, dict):
            errors.append(f"component {idx} must be an object")
            continue
        if not component.get("type"):
            errors.append(f"component {idx} must include type")
        else:
            component_types.append(component["type"])
    if payload.get("human_review_required") and "human_review_disclaimer" not in component_types:
        errors.append("human-review payloads must include human_review_disclaimer")
    urgency = None
    for component in components:
        if isinstance(component, dict) and component.get("type") in {"matter_summary_card", "deadline_timeline"}:
            urgency = str(component.get("urgency", "")).lower()
            if urgency in RISK_URGENCIES:
                break
    if urgency in RISK_URGENCIES and "risk_banner" not in component_types:
        errors.append("high/critical urgency payloads must include risk_banner")
    return not errors, errors
