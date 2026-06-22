# Safety and Compliance

The Matter Intake Triage Agent incorporates a dedicated `Security & Compliance Agent` to ensure safety and privacy.

## Features
1. **PII Redaction**: All intake text is scrubbed for emails, phone numbers, and SSNs before being processed by other agents.
2. **Legal Advice Blocking**: The agent is trained to identify when a user is asking for direct legal advice and flags it, as agents should not provide binding legal counsel.
3. **Audit Logging**: A tool records every time a redaction or policy lookup is performed, providing an audit trail of the system's actions.
