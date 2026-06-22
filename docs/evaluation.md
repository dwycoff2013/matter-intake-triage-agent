# Evaluation

Evaluations are stored in `tests/eval_cases.json`.

We use the ADK Evaluation framework to measure:
1. **Accuracy**: Did the Classifier correctly identify the matter type?
2. **Extraction Recall**: Did the Document Extractor find all dates and parties?
3. **Safety**: Did the Security Reviewer successfully redact all PII?
