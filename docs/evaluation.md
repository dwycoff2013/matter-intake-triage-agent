# Evaluation

Evaluations are stored in `tests/eval_cases.json`.

We use the ADK Evaluation framework to measure:
1. **Accuracy**: Did the Classifier correctly identify the matter type?
2. **Extraction Recall**: Did the Document Extractor find all dates and parties?
3. **Safety**: Did the Security Reviewer successfully redact all PII?


## Evaluation Dimensions

| Dimension | What we evaluate | Example signal |
|---|---|---|
| classification | Whether the intake is assigned the correct matter category and urgency. | Litigation/personal injury and medium urgency for the synthetic slip-and-fall sample. |
| extraction recall | Whether parties, dates, locations, documents, and claims are captured from the intake. | Incident date and requested incident report are present. |
| PII redaction | Whether emails, phone numbers, SSNs, and card-like values are replaced with typed placeholders. | No original PII remains in redacted output. |
| legal-advice refusal/flagging | Whether requests for legal advice are flagged instead of answered as legal advice. | `legal_advice_requested` is true and human review is requested. |
| deadline uncertainty | Whether calculated deadlines are treated as triage aids requiring verification. | Statute-of-limitations review is flagged for attorney confirmation. |
| packet completeness | Whether the final packet includes summary, extracted entities, deadline notes, safety flags, and missing-information checklist. | Sample packet contains all required sections. |

Golden and expected-output fixtures for deterministic sample intake behavior live in `tests/fixtures/`. Synthetic urgency metrics are calculated relative to the fixed fixture date `2026-06-22` (`app.data.synthetic_generator.BASE_DATE`) so results remain reproducible regardless of the current calendar date. Committed 2,500-case demo artifacts live in `outputs/` and can be regenerated with `python -m app.eval.local_eval --n 2500 --out-dir outputs/`.
