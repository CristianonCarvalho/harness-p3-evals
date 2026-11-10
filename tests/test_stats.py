import pytest

from evals.stats import wilson_interval, intervals_overlap


def test_n_zero_has_no_interval():
    assert wilson_interval(0, 0) is None


def test_known_value_56_of_70():
    lo, hi = wilson_interval(56, 70)
    assert lo == pytest.approx(0.692, abs=0.005)
    assert hi == pytest.approx(0.877, abs=0.005)


def test_extremes_stay_inside_0_1():
    lo, hi = wilson_interval(0, 10)
    assert lo == 0.0 and 0.0 < hi < 0.4
    lo, hi = wilson_interval(10, 10)
    assert hi == 1.0 and 0.6 < lo < 1.0


def test_interval_narrows_as_n_grows():
    a = wilson_interval(8, 10); b = wilson_interval(80, 100)
    assert (b[1] - b[0]) < (a[1] - a[0])


def test_overlap():
    assert intervals_overlap((0.1, 0.5), (0.4, 0.9))
    assert not intervals_overlap((0.1, 0.3), (0.4, 0.9))
