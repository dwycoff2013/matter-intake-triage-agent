import pytest
from app.tools.dates import calculate_days_between_dates, extract_dates_regex

def test_calculate_days_between_dates():
    result = calculate_days_between_dates("2026-06-01", "2026-06-15")
    assert result["status"] == "success"
    assert result["days"] == 14

def test_extract_dates_regex():
    text = "The incident happened on 2026-01-15 and the claim was filed 02/01/2026."
    result = extract_dates_regex(text)
    assert result["status"] == "success"
    assert "2026-01-15" in result["dates"]
    assert "02/01/2026" in result["dates"]
