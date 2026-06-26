from datetime import datetime, timezone

from app.tools.audit_log import write_audit_log


class FakeToolContext:
    def __init__(self):
        self.state = {}


def test_write_audit_log_uses_current_utc_timestamp_by_default():
    context = FakeToolContext()
    result = write_audit_log("REDACTION", "demo", context)  # type: ignore[arg-type]
    timestamp = context.state["audit_logs"][0]["timestamp"]
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    assert result["status"] == "success"
    assert parsed.tzinfo == timezone.utc


def test_write_audit_log_allows_deterministic_timestamp_argument():
    context = FakeToolContext()
    write_audit_log("REDACTION", "demo", context, timestamp="2026-06-22T00:00:00Z")  # type: ignore[arg-type]
    assert context.state["audit_logs"][0]["timestamp"] == "2026-06-22T00:00:00Z"


def test_write_audit_log_allows_state_fixed_timestamp():
    context = FakeToolContext()
    context.state["fixed_audit_timestamp"] = "2026-06-22T01:02:03Z"
    write_audit_log("REDACTION", "demo", context)  # type: ignore[arg-type]
    assert context.state["audit_logs"][0]["timestamp"] == "2026-06-22T01:02:03Z"
