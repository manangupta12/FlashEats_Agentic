from backend.services.risk import at_risk_orders, is_at_risk


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


def test_at_risk_orders_keeps_only_qualifying_orders():
    orders = [
        make_order(order_id="FE-1", estimated_delay_minutes=18),
        make_order(order_id="FE-2", estimated_delay_minutes=9),
        make_order(order_id="FE-3", status="DELIVERED", estimated_delay_minutes=30),
        make_order(order_id="FE-4", estimated_delay_minutes=None),
    ]
    assert [o["order_id"] for o in at_risk_orders(orders)] == ["FE-1"]


def test_at_risk_orders_sorts_most_delayed_first():
    orders = [
        make_order(order_id="FE-1", estimated_delay_minutes=10),
        make_order(order_id="FE-2", estimated_delay_minutes=25),
        make_order(order_id="FE-3", estimated_delay_minutes=14),
    ]
    assert [o["order_id"] for o in at_risk_orders(orders)] == [
        "FE-2", "FE-3", "FE-1",
    ]


def test_at_risk_orders_ties_break_on_order_id():
    orders = [
        make_order(order_id="FE-9", estimated_delay_minutes=15),
        make_order(order_id="FE-2", estimated_delay_minutes=15),
    ]
    assert [o["order_id"] for o in at_risk_orders(orders)] == ["FE-2", "FE-9"]


def test_at_risk_orders_empty_input_returns_empty_list():
    assert at_risk_orders([]) == []
