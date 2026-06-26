"""Local A2A-style router demonstration for LexTriage."""

from __future__ import annotations

from app.protocols.a2a import A2AResponseEnvelope, A2ATaskEnvelope
from app.tools.redaction import redact_pii

_ROUTE = [
    ("security_reviewer", "redact_pii", "application/json"),
    ("intake_classifier", "classify_matter", "application/json"),
    ("document_extractor", "extract_entities", "application/json"),
    ("deadline_triage", "extract_dates", "application/json"),
    ("packet_writer", "create_intake_packet", "application/vnd.lextriage.packet+json"),
]


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
        or matter_area
        in {
            "Criminal Defense",
            "Immigration Defense",
            "Family / Domestic Law",
            "Civil Rights",
        }
    )


def _minimized_text(case: dict) -> str:
    """Return redacted/minimized intake text for downstream extraction.

    The document extractor needs enough narrative context to identify dates,
    document types, and entities, but it must not receive the full raw case
    object. Prefer the redaction tool and fall back to deterministic truncation
    if the tool is unavailable or returns an unexpected shape.
    """

    source_text = str(case.get("intake_text") or case.get("summary") or "")
    if not source_text:
        return ""
    try:
        redaction_result = redact_pii(source_text)
        redacted_text = redaction_result.get("redacted_text")
        if isinstance(redacted_text, str):
            return redacted_text[:2000]
    except Exception:
        pass
    return source_text[:1000]


def _task_payload_for_agent(
    to_agent: str, case: dict, case_id: str
) -> tuple[dict, str]:
    if to_agent == "security_reviewer":
        return {
            "case_id": case_id,
            "intake_text": str(case.get("intake_text") or ""),
            "raw_intake_allowed": True,
        }, "raw_intake_allowed"
    if to_agent == "document_extractor":
        return {
            "case_id": case_id,
            "redacted_or_minimized_text": _minimized_text(case),
        }, "redacted_or_minimized"
    if to_agent in {"intake_classifier", "deadline_triage"}:
        return {
            "case_id": case_id,
            "matter_area": case.get("matter_area"),
            "matter_subtype": case.get("matter_subtype"),
            "expected_urgency": case.get("expected_urgency") or case.get("urgency"),
            "human_review_required": _human_review_required(case),
        }, "redacted_or_minimized"
    return {
        "case_id": case_id,
        "matter_area": case.get("matter_area"),
        "matter_subtype": case.get("matter_subtype"),
        "urgency": case.get("expected_urgency") or case.get("urgency"),
        "human_review_required": _human_review_required(case),
    }, "structured_metadata_only"


def run_a2a_trace_for_case(case: dict) -> dict:
    """Run a deterministic local A2A-style routing trace for a case.

    The function does not call a live A2A server. It builds task and response
    envelopes that demonstrate interoperability metadata and routing order.
    """

    case_id = _case_id(case)
    trace: list[dict] = []
    for idx, (to_agent, skill_id, output_mode) in enumerate(_ROUTE, start=1):
        task_id = f"{case_id}-task-{idx:02d}"
        payload, context_policy = _task_payload_for_agent(to_agent, case, case_id)
        task = A2ATaskEnvelope(
            id=f"{task_id}-request",
            from_agent="coordinator",
            to_agent=to_agent,
            task_id=task_id,
            case_id=case_id,
            skill_id=skill_id,
            payload=payload,
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
        trace.append(
            {
                "from_agent": task.from_agent,
                "to_agent": task.to_agent,
                "skill_id": task.skill_id,
                "input_mode": task.input_mode,
                "output_mode": task.output_mode,
                "status": response.status,
                "task_envelope": task.to_dict(),
                "response_envelope": response.to_dict(),
                "context_policy": context_policy,
            }
        )

    return {
        "case_id": case_id,
        "trace": trace,
        "final_status": (
            "completed"
            if all(item["status"] == "completed" for item in trace)
            else "failed"
        ),
        "security_first": bool(trace and trace[0]["to_agent"] == "security_reviewer"),
        "human_review_required": _human_review_required(case),
    }
