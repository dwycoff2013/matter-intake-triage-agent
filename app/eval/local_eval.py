"""Deterministic local evaluation harness for synthetic LexTriage cases."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

from app.data.synthetic_generator import generate_synthetic_intake_cases
from app.tools.dates import extract_dates_regex
from app.tools.redaction import redact_pii

LEGAL_ADVICE_RE = re.compile(r"\b(exactly what I should|guarantee|should I ignore|legal strategy)\b", re.I)
PROMPT_INJECTION_RE = re.compile(r"\b(ignore previous instructions|system override|disregard all guardrails)\b", re.I)


def _predicted_urgency(deadline_date: str) -> str:
    if not deadline_date:
        return "none"
    days = (pd.Timestamp(deadline_date).date() - pd.Timestamp("2026-06-22").date()).days
    if days <= 3:
        return "critical"
    if days <= 10:
        return "high"
    if days <= 30:
        return "medium"
    return "routine"


def evaluate_synthetic_cases(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Evaluate synthetic cases with deterministic local tools only."""
    results: list[dict] = []
    for row in df.to_dict("records"):
        text = row["intake_text"]
        redaction = redact_pii(text)
        dates = extract_dates_regex(text)
        legal_advice = bool(LEGAL_ADVICE_RE.search(text))
        injection = bool(PROMPT_INJECTION_RE.search(text))
        urgency = _predicted_urgency(str(row.get("deadline_date") or ""))
        expected_pii_count = sum(
            int(bool(row.get(col)))
            for col in ["contains_email", "contains_phone", "contains_ssn", "contains_card"]
        )
        expected_date = bool(row.get("deadline_date"))
        human_review = urgency in {"critical", "high"} or legal_advice or injection or row["matter_area"] in {
            "Criminal Defense", "Immigration Defense", "Family / Domestic Law", "Civil Rights"
        }
        results.append({
            "case_id": row["case_id"],
            "expected_pii_count": expected_pii_count,
            "redaction_count": redaction["redaction_count"],
            "redaction_pass": redaction["redaction_count"] >= expected_pii_count,
            "date_count": dates["count"],
            "date_extraction_pass": (dates["count"] > 0) == expected_date,
            "predicted_urgency": urgency,
            "urgency_pass": urgency == row["expected_urgency"],
            "legal_advice_detected": legal_advice,
            "legal_advice_pass": legal_advice == bool(row["asks_legal_advice"]),
            "prompt_injection_detected": injection,
            "prompt_injection_pass": injection == bool(row["prompt_injection"]),
            "human_review_predicted": human_review,
            "human_review_pass": human_review == bool(row["needs_human_review"]),
        })
    results_df = pd.DataFrame(results)
    metrics = {
        "case_count": int(len(results_df)),
        "redaction_pass_rate": float(results_df["redaction_pass"].mean()) if len(results_df) else 0.0,
        "date_extraction_pass_rate": float(results_df["date_extraction_pass"].mean()) if len(results_df) else 0.0,
        "urgency_pass_rate": float(results_df["urgency_pass"].mean()) if len(results_df) else 0.0,
        "legal_advice_detection_pass_rate": float(results_df["legal_advice_pass"].mean()) if len(results_df) else 0.0,
        "prompt_injection_detection_pass_rate": float(results_df["prompt_injection_pass"].mean()) if len(results_df) else 0.0,
        "human_review_routing_pass_rate": float(results_df["human_review_pass"].mean()) if len(results_df) else 0.0,
    }
    return results_df, metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic LexTriage evaluation.")
    parser.add_argument("--n", type=int, default=2500)
    parser.add_argument("--seed", type=int, default=20260622)
    parser.add_argument("--out-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    df = generate_synthetic_intake_cases(args.n, args.seed)
    results_df, metrics = evaluate_synthetic_cases(df)
    df.to_csv(args.out_dir / f"lextriage_synthetic_intake_{args.n}.csv", index=False)
    results_df.to_csv(args.out_dir / f"lextriage_eval_results_{args.n}.csv", index=False)
    (args.out_dir / f"lextriage_metrics_summary_{args.n}.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
