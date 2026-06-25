from app.ui.a2ui_payloads import build_a2ui_intake_payload, validate_a2ui_payload


def _case(**overrides):
    case = {
        "case_id": "SYN-TEST",
        "matter_area": "Employment",
        "matter_subtype": "wage theft",
        "expected_urgency": "routine",
        "deadline_date": "2026-08-01",
        "needs_human_review": False,
        "intake_text": "Email jane@example.com, phone 555-123-4567, SSN 123-45-6789, card 4111-1111-1111-1111.",
    }
    case.update(overrides)
    return case


def _types(payload):
    return {component["type"] for component in payload["components"]}


def _summary(payload):
    return next(component["summary"] for component in payload["components"] if component["type"] == "matter_summary_card")


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


def test_a2ui_payload_has_privacy_note_and_no_raw_pii_in_summary():
    payload = build_a2ui_intake_payload(_case())
    assert payload["privacy_note"]
    summary = _summary(payload)
    for raw in ("jane@example.com", "555-123-4567", "123-45-6789", "4111-1111-1111-1111"):
        assert raw not in summary


def test_validate_a2ui_payload_rejects_unredacted_pii_in_component_summary():
    payload = build_a2ui_intake_payload(_case())
    valid, errors = validate_a2ui_payload(payload)
    assert valid, errors

    bad_payload = build_a2ui_intake_payload(_case())
    for component in bad_payload["components"]:
        if component["type"] == "matter_summary_card":
            component["summary"] = "Contact jane@example.com or 555-123-4567; SSN 123-45-6789; card 4111111111111111."
    valid, errors = validate_a2ui_payload(bad_payload)
    assert not valid
    assert any("unredacted PII" in error for error in errors)
