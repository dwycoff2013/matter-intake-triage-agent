from app.ui.a2ui_payloads import build_a2ui_intake_payload, validate_a2ui_payload


def _case(**overrides):
    case = {
        "case_id": "SYN-TEST",
        "matter_area": "Employment",
        "matter_subtype": "wage theft",
        "expected_urgency": "routine",
        "deadline_date": "2026-08-01",
        "needs_human_review": False,
        "intake_text": "Synthetic non-sensitive intake case.",
    }
    case.update(overrides)
    return case


def _types(payload):
    return {component["type"] for component in payload["components"]}


def test_a2ui_payload_validates_for_normal_case():
    payload = build_a2ui_intake_payload(_case())
    valid, errors = validate_a2ui_payload(payload)
    assert valid, errors


def test_a2ui_payload_validates_for_human_review_case_and_disclaimer():
    payload = build_a2ui_intake_payload(_case(needs_human_review=True, asks_legal_advice=True))
    valid, errors = validate_a2ui_payload(payload)
    assert valid, errors
    assert "human_review_disclaimer" in _types(payload)


def test_high_or_critical_case_includes_risk_banner():
    payload = build_a2ui_intake_payload(_case(expected_urgency="critical", needs_human_review=True))
    valid, errors = validate_a2ui_payload(payload)
    assert valid, errors
    assert "risk_banner" in _types(payload)
