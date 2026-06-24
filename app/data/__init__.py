"""Synthetic data generation utilities for LexTriage."""

__all__ = ["generate_synthetic_intake_cases"]


def __getattr__(name: str):
    if name == "generate_synthetic_intake_cases":
        from app.data.synthetic_generator import generate_synthetic_intake_cases

        return generate_synthetic_intake_cases
    raise AttributeError(name)
