import pytest

from backend.services.risk import is_at_risk


def make_order(**overrides):
    order = {
        "status": "ACTIVE",
        "estimated_delay_minutes": 12,
    }
    order.update(overrides)
    return order


@pytest.mark.parametrize("delay", [10, 11, 60])
def test_active_order_at_or_above_threshold_is_at_risk(delay):
    assert is_at_risk(make_order(estimated_delay_minutes=delay)) is True


@pytest.mark.parametrize("delay", [-1, 0, 9, None])
def test_active_order_below_threshold_or_unknown_delay_is_not_at_risk(delay):
    assert is_at_risk(make_order(estimated_delay_minutes=delay)) is False


@pytest.mark.parametrize("status", ["DELIVERED", "CANCELLED", "PREPARING"])
def test_non_active_order_is_not_actionable_risk(status):
    assert is_at_risk(
        make_order(status=status, estimated_delay_minutes=25)
    ) is False


def test_missing_delay_is_not_classified_as_risk():
    order = make_order()
    del order["estimated_delay_minutes"]

    assert is_at_risk(order) is False


def test_missing_status_is_not_classified_as_risk():
    order = make_order()
    del order["status"]

    assert is_at_risk(order) is False
