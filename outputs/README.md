# Generated evaluation artifacts

This directory contains committed demo artifacts generated from deterministic synthetic data.

Current committed 2,500-case artifacts can be regenerated with:

```bash
python -m app.eval.local_eval --n 2500 --out-dir outputs/
```

The synthetic generator and eval harness use the fixed fixture date `2026-06-22` so metrics are reproducible across calendar dates. New ad hoc output files under this directory are ignored by default unless intentionally force-added for a release or demo submission.
