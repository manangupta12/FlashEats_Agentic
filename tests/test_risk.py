import pytest

from backend.services.risk import is_at_risk


def make_order(**overrides):
    order = {
        "status": "ACTIVE",
        "estimated_delay_minutes": 12,
    }
    order.update(overrides)
    return order


@pytest.mark.parametrize("delay", [10, 11, 30])
def test_active_orders_at_or_above_threshold_are_at_risk(delay):
    assert is_at_risk(make_order(estimated_delay_minutes=delay)) is True


@pytest.mark.parametrize("delay", [-5, 0, 9, None])
def test_active_orders_below_threshold_or_missing_delay_are_not_at_risk(delay):
    assert is_at_risk(make_order(estimated_delay_minutes=delay)) is False


@pytest.mark.parametrize("status", ["DELIVERED", "CANCELLED", "PREPARING"])
def test_non_active_orders_are_not_at_risk_even_with_large_delay(status):
    assert is_at_risk(
        make_order(status=status, estimated_delay_minutes=25)
    ) is False
