from backend.services.risk import get_at_risk_orders, is_at_risk


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


def test_get_at_risk_orders_includes_active_risky_orders():
    orders = [
        make_order(order_id="A", estimated_delay_minutes=12),
        make_order(order_id="B", estimated_delay_minutes=30),
    ]
    result = get_at_risk_orders(orders)
    assert {o["order_id"] for o in result} == {"A", "B"}


def test_get_at_risk_orders_excludes_completed_and_cancelled():
    orders = [
        make_order(order_id="A", status="DELIVERED", estimated_delay_minutes=25),
        make_order(order_id="B", status="CANCELLED", estimated_delay_minutes=25),
        make_order(order_id="C", status="ACTIVE", estimated_delay_minutes=25),
    ]
    result = get_at_risk_orders(orders)
    assert [o["order_id"] for o in result] == ["C"]


def test_get_at_risk_orders_excludes_unknown_delay():
    orders = [
        make_order(order_id="A", estimated_delay_minutes=None),
        make_order(order_id="B", estimated_delay_minutes=15),
    ]
    result = get_at_risk_orders(orders)
    assert [o["order_id"] for o in result] == ["B"]


def test_get_at_risk_orders_includes_delay_at_exactly_ten():
    orders = [make_order(order_id="A", estimated_delay_minutes=10)]
    result = get_at_risk_orders(orders)
    assert [o["order_id"] for o in result] == ["A"]


def test_get_at_risk_orders_sorted_by_delay_descending():
    orders = [
        make_order(order_id="A", estimated_delay_minutes=10),
        make_order(order_id="B", estimated_delay_minutes=40),
        make_order(order_id="C", estimated_delay_minutes=15),
    ]
    result = get_at_risk_orders(orders)
    assert [o["order_id"] for o in result] == ["B", "C", "A"]
