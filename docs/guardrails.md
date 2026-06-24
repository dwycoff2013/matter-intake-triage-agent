# Guardrails and Callback Strategy

LexTriage's intended ADK hardening model uses callbacks/plugins to keep model behavior inside deterministic, auditable boundaries.

## `before_model_callback`

- Redact or minimize PII before model exposure.
- Block or quarantine prompt-injection attempts.
- Flag legal-advice requests so the response can refuse advice and route to human review.

## `before_tool_callback`

- Allow only approved local tools from the MCP-style deterministic tool layer.
- Block external network calls in demo mode.
- Record the requested tool name, arguments metadata, and policy decision for audit review.

## `after_agent_callback`

- Require a human-review disclaimer in final packets.
- Write an audit event for packet generation and routing decisions.
- Assert that required structured packet fields exist before returning a result.

## Current implementation status

| Guardrail | Implemented? | Location | Notes |
|---|---:|---|---|
| PII redaction tool | Yes | `app/tools/redaction.py` | Deterministic regex redaction for email, phone, SSN, and payment-card-like strings. |
| Date extraction and date math | Yes | `app/tools/dates.py` | Deterministic local date parsing and interval calculation. |
| Legal-advice detection in local eval | Yes | `app/eval/local_eval.py` | Regex evaluation harness flag; planned callback integration. |
| Prompt-injection detection in local eval | Yes | `app/eval/local_eval.py` | Regex evaluation harness flag; planned callback integration. |
| `before_model_callback` | Planned | ADK integration layer | Design-only in this pass. |
| `before_tool_callback` allowlist | Planned | ADK integration layer | Design-only in this pass. |
| `after_agent_callback` packet assertions | Planned | ADK integration layer | Design-only in this pass. |
| Audit logging tool | Yes | `app/tools/audit_log.py` | Local tool exists; callback wiring is planned. |
