from backend.services.risk import build_at_risk_queue, is_at_risk


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


def make_queue_order(order_id, delay, promised_eta="20:00", status="ACTIVE"):
    return make_order(
        order_id=order_id,
        status=status,
        estimated_delay_minutes=delay,
        promised_eta=promised_eta,
    )


def queue_ids(orders):
    return [order["order_id"] for order in build_at_risk_queue(orders)]


def test_queue_excludes_orders_that_are_not_at_risk():
    orders = [
        make_queue_order("KEEP", 10),
        make_queue_order("DELIVERED", 25, status="DELIVERED"),
        make_queue_order("CANCELLED", 21, status="CANCELLED"),
        make_queue_order("UNKNOWN", None),
        make_queue_order("BELOW", 9),
        make_queue_order("EARLY", -3),
    ]
    assert queue_ids(orders) == ["KEEP"]


def test_queue_puts_largest_delay_first():
    orders = [
        make_queue_order("A", 10),
        make_queue_order("B", 18),
        make_queue_order("C", 14),
    ]
    assert queue_ids(orders) == ["B", "C", "A"]


def test_queue_breaks_delay_ties_by_earliest_promised_eta():
    orders = [
        make_queue_order("LATER", 15, promised_eta="20:30"),
        make_queue_order("EARLIER", 15, promised_eta="19:45"),
    ]
    assert queue_ids(orders) == ["EARLIER", "LATER"]


def test_queue_breaks_remaining_ties_by_order_id():
    orders = [
        make_queue_order("FE-2", 15, promised_eta="20:00"),
        make_queue_order("FE-1", 15, promised_eta="20:00"),
    ]
    assert queue_ids(orders) == ["FE-1", "FE-2"]


def test_queue_returns_orders_unchanged():
    order = make_queue_order("FE-1", 12)
    assert build_at_risk_queue([order]) == [dict(order)]
    assert "risk_score" not in build_at_risk_queue([order])[0]


def test_empty_input_gives_empty_queue():
    assert build_at_risk_queue([]) == []
