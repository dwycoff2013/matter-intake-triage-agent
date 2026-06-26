"""Audit logging tool for deterministic demos and ADK sessions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from google.adk.tools import ToolContext


def _utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def write_audit_log(
    action: str,
    details: str,
    tool_context: ToolContext,
    timestamp: str | None = None,
) -> dict:
    """Write an audit log entry to ADK session state.

    Tests may pass ``timestamp`` or set ``tool_context.state['fixed_audit_timestamp']``
    to keep assertions deterministic. Runtime calls use the current UTC time.
    """
    fixed_state_timestamp: Any = tool_context.state.get("fixed_audit_timestamp")
    log_entry = {
        "action": action,
        "details": details,
        "timestamp": timestamp
        or (str(fixed_state_timestamp) if fixed_state_timestamp else _utc_now_iso()),
    }

    if "audit_logs" not in tool_context.state:
        tool_context.state["audit_logs"] = []

    tool_context.state["audit_logs"].append(log_entry)

    return {"status": "success", "message": "Audit log recorded successfully."}
