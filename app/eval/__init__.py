"""Deterministic local evaluation utilities for LexTriage."""

__all__ = ["evaluate_synthetic_cases"]


def __getattr__(name: str):
    if name == "evaluate_synthetic_cases":
        from app.eval.local_eval import evaluate_synthetic_cases

        return evaluate_synthetic_cases
    raise AttributeError(name)
