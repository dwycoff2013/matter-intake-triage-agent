import pandas as pd

from app.data.synthetic_generator import generate_synthetic_intake_cases


def test_generator_returns_requested_row_count():
    df = generate_synthetic_intake_cases(n_cases=37)
    assert len(df) == 37


def test_generator_is_deterministic_for_same_seed():
    df1 = generate_synthetic_intake_cases(n_cases=50, seed=123)
    df2 = generate_synthetic_intake_cases(n_cases=50, seed=123)
    pd.testing.assert_frame_equal(df1, df2)


def test_generator_includes_required_matter_area_breadth():
    df = generate_synthetic_intake_cases(n_cases=250)
    areas = set(df["matter_area"])
    assert len(areas) >= 15
    assert {
        "Criminal Defense",
        "Bankruptcy",
        "Personal Injury",
        "Family / Domestic Law",
        "Housing / Landlord-Tenant",
    }.issubset(areas)


def test_generator_uses_obviously_synthetic_domain():
    df = generate_synthetic_intake_cases(n_cases=20)
    assert df["intake_text"].str.contains("examplelegal.test", regex=False).any()
