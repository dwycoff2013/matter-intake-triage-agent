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
