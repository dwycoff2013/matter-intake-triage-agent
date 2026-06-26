import pytest
from app.tools.redaction import redact_pii

def test_redact_pii():
    text = "My email is test@example.com and phone is 555-123-4567. SSN: 123-45-6789"
    result = redact_pii(text)
    assert result["status"] == "success"
    assert "test@example.com" not in result["redacted_text"]
    assert "[EMAIL REDACTED]" in result["redacted_text"]
    assert "555-123-4567" not in result["redacted_text"]
    assert "[PHONE REDACTED]" in result["redacted_text"]
    assert "123-45-6789" not in result["redacted_text"]
    assert "[SSN REDACTED]" in result["redacted_text"]


def test_redaction_covers_supported_payment_card_pattern():
    result = redact_pii("Card 4111-1111-1111-1111 belongs in a synthetic fixture.")
    assert "4111-1111-1111-1111" not in result["redacted_text"]
    assert "[PAYMENT REDACTED]" in result["redacted_text"]


def test_redaction_does_not_claim_to_remove_names_or_street_addresses():
    text = "Jane Example lives at 123 Main Street. Email jane@example.com."
    result = redact_pii(text)
    assert "Jane Example" in result["redacted_text"]
    assert "123 Main Street" in result["redacted_text"]
    assert "jane@example.com" not in result["redacted_text"]
