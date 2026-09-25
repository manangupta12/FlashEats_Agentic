from backend.services.orders import get_at_risk_orders
from backend.services.risk import is_at_risk


def make_order(**overrides):
    order = {
        "status": "ACTIVE",
        "estimated_delay_minutes": 12,
    }
    order.update(overrides)
    return order


def test_active_order_at_threshold_is_at_risk():
    assert is_at_risk(make_order(estimated_delay_minutes=10)) is True


def test_active_order_below_threshold_is_not_at_risk():
    assert is_at_risk(make_order(estimated_delay_minutes=9)) is False


def test_completed_late_order_is_not_actionable_risk():
    assert is_at_risk(
        make_order(status="DELIVERED", estimated_delay_minutes=25)
    ) is False


def test_unknown_delay_is_not_classified_as_risk():
    assert is_at_risk(
        make_order(estimated_delay_minutes=None)
    ) is False


def test_get_at_risk_orders_filters_and_sorts_correctly():
    at_risk_orders = get_at_risk_orders()
    assert len(at_risk_orders) == 3
    order_ids = [o["order_id"] for o in at_risk_orders]
    assert order_ids == ["FE-48291", "FE-48293", "FE-48297"]
    delays = [o["estimated_delay_minutes"] for o in at_risk_orders]
    assert delays == [18, 14, 10]

