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
