# Guardrails and Callback Strategy

LexTriage combines implemented deterministic local guardrails with a planned ADK callback hardening model. Local tests and demos run without model calls; future live ADK callbacks should enforce the same policies at model/tool boundaries.

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
| Legal-advice detection | Yes | `app/guardrails.py` | Deterministic regex guardrail used by local eval and UI/protocol paths. |
| Prompt-injection detection | Yes | `app/guardrails.py` | Deterministic regex guardrail used by local eval and UI/protocol paths. |
| Human-review routing | Yes | `app/guardrails.py` | Routes urgent, sensitive, legal-advice, and prompt-injection cases for review. |
| Final packet common-PII validation | Yes | `app/guardrails.py` | Checks generated text for supported common PII patterns and disclaimer text. |
| `before_model_callback` | Planned | ADK integration layer | Future live-model enforcement of implemented local guardrail policies. |
| `before_tool_callback` allowlist | Planned | ADK integration layer | Design-only in this pass. |
| `after_agent_callback` packet assertions | Planned | ADK integration layer | Future callback should call the deterministic packet validator. |
| Audit logging tool | Yes | `app/tools/audit_log.py` | Local tool exists; callback wiring is planned. |
