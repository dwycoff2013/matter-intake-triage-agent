from app.ui.a2ui_payloads import build_a2ui_intake_payload
from app.ui.a2ui_renderers import render_a2ui_payload_html


def _case(**overrides):
    case = {
        "case_id": "SYN-HTML",
        "matter_area": "Employment",
        "matter_subtype": "wrongful termination",
        "expected_urgency": "high",
        "deadline_date": "2026-08-01",
        "needs_human_review": True,
        "intake_text": "<script>alert(1)</script> Email jane@example.com phone 555-123-4567 SSN 123-45-6789 card 4111-1111-1111-1111.",
    }
    case.update(overrides)
    return case


def test_render_a2ui_payload_html_returns_string_with_case_id_and_headings():
    payload = build_a2ui_intake_payload(_case())
    rendered = render_a2ui_payload_html(payload)
    assert isinstance(rendered, str)
    assert "SYN-HTML" in rendered
    assert "Matter Summary" in rendered
    assert "Deadline Timeline" in rendered
    assert "Safety Flags" in rendered


def test_render_a2ui_payload_html_escapes_obvious_html_input():
    payload = build_a2ui_intake_payload(_case(matter_subtype='<img src=x onerror="alert(1)">'))
    rendered = render_a2ui_payload_html(payload)
    assert '<img src=x onerror="alert(1)">' not in rendered
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;" in rendered


def test_payload_builder_prevents_pii_in_rendered_matter_summary():
    payload = build_a2ui_intake_payload(_case())
    rendered = render_a2ui_payload_html(payload)
    for raw in ("jane@example.com", "555-123-4567", "123-45-6789", "4111-1111-1111-1111"):
        assert raw not in rendered
