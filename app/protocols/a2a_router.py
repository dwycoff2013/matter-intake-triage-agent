"""Local A2A-style router demonstration for LexTriage."""

from __future__ import annotations

from app.protocols.a2a import A2AResponseEnvelope, A2ATaskEnvelope

_ROUTE = [
    ("security_reviewer", "redact_pii", "application/json"),
    ("intake_classifier", "classify_matter", "application/json"),
    ("document_extractor", "extract_entities", "application/json"),
    ("deadline_triage", "extract_dates", "application/json"),
    ("packet_writer", "create_intake_packet", "application/vnd.lextriage.packet+json"),
]

_CONTEXT_POLICIES = {
    "security_reviewer": "raw_intake_allowed",
    "intake_classifier": "structured_metadata_only",
    "document_extractor": "redacted_or_minimized",
    "deadline_triage": "structured_metadata_only",
    "packet_writer": "structured_metadata_only",
}


def _case_id(case: dict) -> str:
    return str(case.get("case_id") or case.get("id") or "CASE-UNKNOWN")


def _human_review_required(case: dict) -> bool:
    urgency = str(case.get("expected_urgency") or case.get("urgency") or "").lower()
    matter_area = str(case.get("matter_area") or "")
    return bool(
        case.get("needs_human_review")
        or case.get("human_review_required")
        or case.get("asks_legal_advice")
        or case.get("prompt_injection")
        or urgency in {"critical", "high"}
        or matter_area in {"Criminal Defense", "Immigration Defense", "Family / Domestic Law", "Civil Rights"}
    )


def _safety_flags_summary(case: dict) -> dict:
    return {
        "asks_legal_advice": bool(case.get("asks_legal_advice")),
        "prompt_injection": bool(case.get("prompt_injection")),
        "contains_pii": bool(
            case.get("contains_email")
            or case.get("contains_phone")
            or case.get("contains_ssn")
            or case.get("contains_card")
        ),
        "needs_human_review": _human_review_required(case),
    }


def _payload_for_agent(case: dict, to_agent: str) -> dict:
    """Return role-specific minimized context for a routed A2A task."""

    case_id = _case_id(case)
    base = {
        "case_id": case_id,
        "matter_area": case.get("matter_area"),
        "matter_subtype": case.get("matter_subtype"),
    }
    if to_agent == "security_reviewer":
        return {**base, "intake_text": case.get("intake_text", "")}
    if to_agent == "intake_classifier":
        return {
            **base,
            "expected_urgency": case.get("expected_urgency") or case.get("urgency"),
            "deadline_date": case.get("deadline_date") or None,
            "safety_flags": _safety_flags_summary(case),
        }
    if to_agent == "document_extractor":
        return {**base, "deadline_date": case.get("deadline_date") or None}
    if to_agent == "deadline_triage":
        return {
            "case_id": case_id,
            "deadline_date": case.get("deadline_date") or None,
            "expected_urgency": case.get("expected_urgency") or case.get("urgency"),
        }
    if to_agent == "packet_writer":
        return {
            **base,
            "expected_urgency": case.get("expected_urgency") or case.get("urgency"),
            "deadline_date": case.get("deadline_date") or None,
            "needs_human_review": _human_review_required(case),
            "safety_flags": _safety_flags_summary(case),
        }
    return {"case_id": case_id}


def run_a2a_trace_for_case(case: dict) -> dict:
    """Run a deterministic local A2A-style routing trace for a case.

    The function does not call a live A2A server. It builds task and response
    envelopes that demonstrate interoperability metadata and routing order.
    """

    case_id = _case_id(case)
    trace: list[dict] = []
    for idx, (to_agent, skill_id, output_mode) in enumerate(_ROUTE, start=1):
        task_id = f"{case_id}-task-{idx:02d}"
        context_policy = _CONTEXT_POLICIES[to_agent]
        task = A2ATaskEnvelope(
            id=f"{task_id}-request",
            from_agent="coordinator",
            to_agent=to_agent,
            task_id=task_id,
            case_id=case_id,
            skill_id=skill_id,
            payload=_payload_for_agent(case, to_agent),
            input_mode="application/json",
            output_mode=output_mode,
        )
        response = A2AResponseEnvelope(
            id=f"{task_id}-response",
            from_agent=to_agent,
            to_agent="coordinator",
            task_id=task_id,
            case_id=case_id,
            skill_id=skill_id,
            payload={"case_id": case_id, "result": "local protocol demo completed"},
            output_mode=output_mode,
        )
        trace.append({
            "from_agent": task.from_agent,
            "to_agent": task.to_agent,
            "skill_id": task.skill_id,
            "context_policy": context_policy,
            "input_mode": task.input_mode,
            "output_mode": task.output_mode,
            "status": response.status,
            "task_envelope": task.to_dict(),
            "response_envelope": response.to_dict(),
        })

    return {
        "case_id": case_id,
        "trace": trace,
        "final_status": "completed" if all(item["status"] == "completed" for item in trace) else "failed",
        "security_first": bool(trace and trace[0]["to_agent"] == "security_reviewer"),
        "human_review_required": _human_review_required(case),
    }
