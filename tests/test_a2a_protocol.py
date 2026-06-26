from app.data.synthetic_generator import generate_synthetic_intake_cases
from app.protocols.a2a import build_lextriage_agent_cards
from app.protocols.a2a_router import run_a2a_trace_for_case


def test_all_expected_agent_cards_exist():
    cards = build_lextriage_agent_cards()
    assert set(cards) == {
        "coordinator",
        "security_reviewer",
        "intake_classifier",
        "document_extractor",
        "deadline_triage",
        "packet_writer",
    }


def test_security_reviewer_card_includes_pii_redaction_skill():
    card = build_lextriage_agent_cards()["security_reviewer"]
    assert any(skill.id == "redact_pii" for skill in card.skills)


def test_a2a_trace_security_first_packet_writer_and_completed():
    case = generate_synthetic_intake_cases(n_cases=1).iloc[0].to_dict()
    trace_result = run_a2a_trace_for_case(case)
    assert trace_result["trace"][0]["to_agent"] == "security_reviewer"
    assert any(item["to_agent"] == "packet_writer" for item in trace_result["trace"])
    assert trace_result["final_status"] == "completed"


def test_a2a_trace_uses_role_specific_minimized_payloads():
    case = generate_synthetic_intake_cases(n_cases=1).iloc[0].to_dict()
    case["intake_text"] = "Call Jane at 555-123-4567 about the lease notice by Friday."
    trace = run_a2a_trace_for_case(case)["trace"]
    by_agent = {item["to_agent"]: item for item in trace}

    security_payload = by_agent["security_reviewer"]["task_envelope"]["payload"]
    assert security_payload["intake_text"] == case["intake_text"]
    assert security_payload["raw_intake_allowed"] is True
    assert by_agent["security_reviewer"]["context_policy"] == "raw_intake_allowed"

    for agent in ["intake_classifier", "deadline_triage", "packet_writer"]:
        payload = by_agent[agent]["task_envelope"]["payload"]
        assert "intake_text" not in payload
        assert "case" not in payload

    document_payload = by_agent["document_extractor"]["task_envelope"]["payload"]
    assert "case" not in document_payload
    assert "intake_text" not in document_payload
    assert "redacted_or_minimized_text" in document_payload
    assert "555-123-4567" not in document_payload["redacted_or_minimized_text"]
    assert by_agent["document_extractor"]["context_policy"] == "redacted_or_minimized"

    later_policies = [item["context_policy"] for item in trace[1:]]
    assert all(
        policy in {"redacted_or_minimized", "structured_metadata_only"}
        for policy in later_policies
    )
