# LexTriage: Matter Intake Triage Agent

LexTriage demonstrates agent reliability through deterministic boundaries: graph-style orchestration, MCP-style local tools, context minimization, implemented local guardrails, planned ADK callbacks, trajectory evaluation, and human-reviewable legal intake packets.

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

These commands were smoke-checked against `google-adk==2.3.*` and require appropriate local credentials such as `GOOGLE_API_KEY`. The no-credential smoke demo is `python -m app.agent`; it deliberately avoids importing ADK modules or making model calls.

## Deterministic local evaluation

```bash
python -m app.data.synthetic_generator --n 2500 --out outputs/lextriage_synthetic_intake_2500.csv
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
| `assess_intake()` / `validate_final_packet()` | `app/guardrails.py` |

## Kaggle notebook relationship

The Kaggle notebook should import repo code, generate 2,500 synthetic cases, run deterministic local eval, chart aggregate metrics, and optionally run ADK cells only when credentials are available. See `notebooks/README.md`.

The ADK eval-set exporter writes a replayable JSON fixture at `eval_sets/lextriage_core_eval.json`. If the active ADK version expects a different `adk eval` schema, adapt the exported `case_id`, `query`, and `expected` fields into that schema while preserving the synthetic case content and deterministic expected labels.

## Concepts from the 5-day intensive

- **Graph/workflow orchestration:** the coordinator routes intake through security, classification, extraction, deadline triage, policy lookup, packet writing, and review.
- **MCP-style tools as deterministic boundaries:** local tools perform redaction, date extraction, date math, policy lookup, calendar mock actions, and audit logging.
- **Context minimization:** downstream agents receive redacted or structured context instead of raw intake whenever possible.
- **Implemented local guardrails:** `app/guardrails.py` performs deterministic common-PII redaction, legal-advice detection, prompt-injection detection, human-review routing, and final packet PII checks for local/eval flows.
- **Planned callback/plugin guardrails:** future ADK callbacks can enforce these policies at live model/tool boundaries, including tool allowlists and demo-mode network blocking.
- **Trajectory/tool-use evaluation:** local eval produces case-level results and metrics that can be compared across runs.
- **Collaborative subagent roles:** specialized agents separate security review, matter classification, document extraction, deadline triage, and packet writing.

## Redaction scope

The demo redaction layer is intentionally regex-based and currently covers email addresses, US-style phone numbers, SSNs, and credit/payment-card-like numbers. It does **not** claim to remove names, street addresses, dates of birth, case numbers, or every jurisdiction-specific identifier. Use synthetic data only.

## Generated artifacts

Committed 2,500-case demo artifacts live in `outputs/` with a manifest in `outputs/README.md`. Regenerate them with `python -m app.eval.local_eval --n 2500 --out-dir outputs/`; urgency metrics use the fixed synthetic fixture date `2026-06-22` for reproducibility. Root-level notebooks have moved under `notebooks/`.

## Testing

```bash
python -m pytest tests -q
```

## License

Apache 2.0
