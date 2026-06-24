"""Export a small replayable LexTriage eval fixture for ADK adaptation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.data.synthetic_generator import generate_synthetic_intake_cases


def export_evalset(n: int = 50, out: Path = Path("eval_sets/lextriage_core_eval.json"), seed: int = 20260622) -> list[dict]:
    pool = generate_synthetic_intake_cases(max(250, n * 5), seed)
    selected = []
    selectors = [
        pool[pool.expected_urgency.isin(["critical", "high"])],
        pool[pool.expected_urgency.eq("none")],
        pool[pool.asks_legal_advice],
        pool[pool.prompt_injection],
        pool[pool.contains_ssn | pool.contains_card],
    ]
    for frame in selectors:
        if not frame.empty:
            selected.append(frame.iloc[0])
    for _, row in pool.drop_duplicates("matter_area").iterrows():
        selected.append(row)
        if len(selected) >= n:
            break
    seen = {row.case_id for row in selected}
    for _, row in pool.iterrows():
        if len(selected) >= n:
            break
        if row.case_id not in seen:
            selected.append(row)
            seen.add(row.case_id)
    records = [{
        "case_id": row.case_id,
        "query": row.intake_text,
        "expected": {
            "matter_area": row.matter_area,
            "matter_subtype": row.matter_subtype,
            "urgency": row.expected_urgency,
            "must_redact_pii": bool(row.contains_email or row.contains_phone or row.contains_ssn or row.contains_card),
            "must_route_to_human": bool(row.needs_human_review),
            "legal_advice_request": bool(row.asks_legal_advice),
            "prompt_injection": bool(row.prompt_injection),
        },
    } for row in selected[:n]]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"schema": "lextriage.replayable_eval.v1", "cases": records}, indent=2), encoding="utf-8")
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a small LexTriage eval fixture.")
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260622)
    parser.add_argument("--out", type=Path, default=Path("eval_sets/lextriage_core_eval.json"))
    args = parser.parse_args()
    records = export_evalset(args.n, args.out, args.seed)
    print(f"Wrote {len(records)} eval cases to {args.out}")


if __name__ == "__main__":
    main()
