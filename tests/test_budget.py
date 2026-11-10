import pytest

from evals.budget import BudgetGuard, BudgetExceeded


def test_charges_accumulate():
    g = BudgetGuard(1.0)
    g.charge(0.25); g.charge(0.25)
    assert g.spent == pytest.approx(0.5)


def test_raises_when_limit_is_reached_or_passed():
    g = BudgetGuard(1.0)
    g.charge(0.9)
    with pytest.raises(BudgetExceeded):
        g.charge(0.1)


def test_raises_when_limit_is_passed_not_only_reached():
    g = BudgetGuard(1.0)
    with pytest.raises(BudgetExceeded):
        g.charge(1.5)


def test_charge_just_below_the_limit_does_not_raise():
    g = BudgetGuard(1.0)
    g.charge(0.999)
    assert g.spent == pytest.approx(0.999)


def test_non_positive_limit_is_rejected():
    with pytest.raises(ValueError):
        BudgetGuard(0)
    with pytest.raises(ValueError):
        BudgetGuard(-1)
