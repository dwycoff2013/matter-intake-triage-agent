# Matter Intake Triage Agent

A modular multi-agent system built with **Google ADK 2.0** for processing legal matter intake emails.

## Architecture

```
User / Demo UI
       │
  Coordinator (Workflow graph)
       │
       ├── Intake Classifier Agent
       │     - classifies matter type and urgency
       │
       ├── Document Extraction Agent  ┐
       │     - extracts parties,      │  (parallel fan-out)
       │       dates, locations,      │
       │       documents, claims      │
       │                              │
       ├── Security & Compliance Agent┘
       │     - redacts PII
       │     - blocks legal-advice requests
       │     - records tool calls
       │
       ├── Deadline Triage Agent
       │     - calculates date intervals
       │     - flags uncertainty
       │     - requires human verification
       │
       └── Packet Writer Agent
             - generates structured intake memo
             - generates missing-info checklist
```

## Tools (MCP-style local layer)

| Tool | Module |
|------|--------|
| `calculate_days_between_dates()` | `app/tools/dates.py` |
| `extract_dates_regex()` | `app/tools/dates.py` |
| `redact_pii()` | `app/tools/redaction.py` |
| `create_mock_calendar_event()` | `app/tools/mock_calendar.py` |
| `lookup_mock_matter_type_policy()` | `app/tools/mock_policy_lookup.py` |
| `write_audit_log()` | `app/tools/audit_log.py` |

## Getting Started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GOOGLE_API_KEY
python -m app.agent     # CLI demo
# or
adk web app             # ADK web UI
```

## Running Tests

```bash
pytest tests/ -v
```

## License

Apache 2.0
