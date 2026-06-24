import pandas as pd

from app.data.synthetic_generator import generate_synthetic_intake_cases
from app.eval.local_eval import evaluate_synthetic_cases


def test_local_eval_returns_dataframe_and_metrics_dict():
    df = generate_synthetic_intake_cases(n_cases=40)
    results, metrics = evaluate_synthetic_cases(df)
    assert isinstance(results, pd.DataFrame)
    assert isinstance(metrics, dict)
    assert len(results) == 40


def test_local_eval_includes_core_metrics():
    df = generate_synthetic_intake_cases(n_cases=80)
    _, metrics = evaluate_synthetic_cases(df)
    assert "redaction_pass_rate" in metrics
    assert "legal_advice_detection_pass_rate" in metrics
    assert "prompt_injection_detection_pass_rate" in metrics
    assert "human_review_routing_pass_rate" in metrics
