# Limitations

1. **Regex Redaction**: The PII redaction relies on simple regular expressions and currently covers email, US-style phone, SSN, and credit/payment-card-like values only. It does not claim to remove names, street addresses, dates of birth, case numbers, or every jurisdiction-specific identifier. In a production environment, this should be replaced with Google Cloud DLP (Data Loss Prevention) API or similar robust models.
2. **Mock Tools**: The calendar and policy tools are currently mocks and do not interact with real external APIs.
3. **Date Formats**: The date extraction regex might miss non-standard date formats or relative dates (e.g., "last Tuesday").

4. **Fixture Clock**: Synthetic eval urgency is measured from the fixed fixture date `2026-06-22`; runtime deadline helpers should receive an explicit current date/clock.
5. **ADK Credentials**: ADK CLI/server commands require `google-adk==2.3.*` and local credentials such as `GOOGLE_API_KEY`; local deterministic tests do not require live model calls.
