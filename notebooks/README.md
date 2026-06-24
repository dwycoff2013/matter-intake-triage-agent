# Kaggle Notebook Integration

The Kaggle notebook should be a reproducible wrapper around repository code, not the only implementation of LexTriage logic.

Recommended flow:

1. Install or import this repository code in the notebook environment.
2. Generate 2,500 synthetic cases with `app.data.synthetic_generator`.
3. Run deterministic local evaluation with `app.eval.local_eval`.
4. Show aggregate charts and a few curated examples from the generated/evaluated data.
5. Optionally run ADK CLI cells if `google-adk` and `GOOGLE_API_KEY` are available.
6. Keep core notebook execution reproducible without credentials or live Gemini calls.

Example credential-free cells:

```bash
python -m app.data.synthetic_generator --n 2500 --out outputs/lextriage_synthetic_intake_2500.csv
python -m app.eval.local_eval --n 2500 --out-dir outputs/
python -m app.eval.export_adk_evalset --n 50 --out eval_sets/lextriage_core_eval.json
```

All data is synthetic. Do not upload real client data, secrets, or confidential legal materials to Kaggle.
