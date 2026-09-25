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


def test_cancelled_order_is_not_actionable_risk():
    assert is_at_risk(
        make_order(status="CANCELLED", estimated_delay_minutes=21)
    ) is False


def test_unknown_delay_is_not_classified_as_risk():
    assert is_at_risk(
        make_order(estimated_delay_minutes=None)
    ) is False

