# Limitations

1. **Regex Redaction**: The PII redaction relies on simple regular expressions. In a production environment, this should be replaced with Google Cloud DLP (Data Loss Prevention) API or similar robust models.
2. **Mock Tools**: The calendar and policy tools are currently mocks and do not interact with real external APIs.
3. **Date Formats**: The date extraction regex might miss non-standard date formats or relative dates (e.g., "last Tuesday").
