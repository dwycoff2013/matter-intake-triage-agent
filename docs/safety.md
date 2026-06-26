# Safety and Compliance

The Matter Intake Triage Agent incorporates a dedicated `Security & Compliance Agent` to ensure safety and privacy.

## Features
1. **Common PII Redaction**: Deterministic regex tools redact email addresses, US-style phone numbers, SSNs, and credit/payment-card-like numbers. This is not comprehensive de-identification and does not claim to remove names, street addresses, dates of birth, or every case/client identifier.
2. **Legal Advice Blocking**: Deterministic guardrails flag requests for direct legal advice and route them to human review instead of treating automated output as binding legal counsel.
3. **Prompt-Injection Detection**: Deterministic guardrails flag common demo prompt-injection phrases such as requests to ignore prior instructions or bypass guardrails.
4. **Human Review Routing**: Urgent, sensitive, legal-advice, and prompt-injection cases require qualified human review before client-facing recommendations.
5. **Audit Logging**: A tool records redaction or policy events with UTC timestamps, while tests can inject fixed timestamps for reproducibility.
