# LexTriage: Matter Intake Triage Agent

LexTriage demonstrates agent reliability through deterministic boundaries: graph-style orchestration, MCP-style local tools, context minimization, safety callbacks/guardrails, trajectory evaluation, and human-reviewable legal intake packets.

## Safety and data disclaimers

LexTriage is a hackathon/demo legal-ops intake aid, not legal advice and not a substitute for attorney review. Use synthetic data only. Do not enter real client data, privileged communications, or secrets. Generated datasets use fictional facts and reserved domains such as `examplelegal.test`.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.agent
python -m pytest tests -q
```

## Canonical ADK commands

The repo exposes the root agent through `agents/lextriage`, which imports `root_agent` from `app.agent`.

```bash
adk run agents/lextriage
adk web agents
adk api_server agents --port 8000
```

These commands require `google-adk` and appropriate local credentials such as `GOOGLE_API_KEY`. The no-credential smoke demo is `python -m app.agent`.

## Deterministic local evaluation

```bash
python -m app.data.synthetic_generator --n 2500 --out data/lextriage_synthetic_intake_2500.csv
python -m app.eval.local_eval --n 2500 --out-dir outputs/
python -m app.eval.export_adk_evalset --n 50 --out eval_sets/lextriage_core_eval.json
```

The eval harness checks PII redaction coverage, date extraction coverage, urgency sanity, legal-advice detection, prompt-injection detection, and human-review routing without requiring a live Gemini/Google API key.

## Architecture

```text
START
  -> Security / PII / Prompt-Injection Gate
  -> Matter Classification
  -> Document and Date Extraction
  -> Deadline Triage
  -> Policy Lookup
  -> Packet Writer
  -> Human Review
```

| Tool | Module |
|------|--------|
| `calculate_days_between_dates()` | `app/tools/dates.py` |
| `extract_dates_regex()` | `app/tools/dates.py` |
| `redact_pii()` | `app/tools/redaction.py` |
| `create_mock_calendar_event()` | `app/tools/mock_calendar.py` |
| `lookup_mock_matter_type_policy()` | `app/tools/mock_policy_lookup.py` |
| `write_audit_log()` | `app/tools/audit_log.py` |

## Kaggle notebook relationship

The Kaggle notebook should import repo code, generate 2,500 synthetic cases, run deterministic local eval, chart aggregate metrics, and optionally run ADK cells only when credentials are available. See `notebooks/README.md`.

The ADK eval-set exporter writes a replayable JSON fixture at `eval_sets/lextriage_core_eval.json`. If the active ADK version expects a different `adk eval` schema, adapt the exported `case_id`, `query`, and `expected` fields into that schema while preserving the synthetic case content and deterministic expected labels.

## Concepts from the 5-day intensive

- **Graph/workflow orchestration:** the coordinator routes intake through security, classification, extraction, deadline triage, policy lookup, packet writing, and review.
- **MCP-style tools as deterministic boundaries:** local tools perform redaction, date extraction, date math, policy lookup, calendar mock actions, and audit logging.
- **Context minimization:** downstream agents receive redacted or structured context instead of raw intake whenever possible.
- **Callback/plugin guardrails:** planned ADK callbacks enforce pre-model redaction, tool allowlists, demo-mode network blocking, and final packet assertions.
- **Trajectory/tool-use evaluation:** local eval produces case-level results and metrics that can be compared across runs.
- **Collaborative subagent roles:** specialized agents separate security review, matter classification, document extraction, deadline triage, and packet writing.

## Testing

```bash
python -m pytest tests -q
```

## License

Apache 2.0
