"""Wilson intervals."""

from src.stats import wilson_interval


def test_bounds_contain_the_proportion_and_stay_inside_zero_and_one():
    low, high = wilson_interval(9, 21)
    assert 0.0 <= low <= (9 / 21) <= high <= 1.0


def test_zero_successes_has_a_zero_lower_bound():
    low, high = wilson_interval(0, 10)
    assert low == 0.0
    assert 0.0 < high < 1.0


def test_empty_denominator():
    assert wilson_interval(0, 0) == (0.0, 0.0)
