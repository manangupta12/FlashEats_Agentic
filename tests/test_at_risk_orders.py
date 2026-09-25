import pytest

from backend.services import orders as orders_service


def make_order(order_id="FE-TEST", **overrides):
    order = {
        "order_id": order_id,
        "status": "ACTIVE",
        "promised_eta": "20:00",
        "current_eta": "20:15",
        "estimated_delay_minutes": 15,
        "restaurant_status": "READY",
        "driver_status": "EN_ROUTE",
        "support_opened": False,
        "previous_intervention": None,
    }
    order.update(overrides)
    return order


@pytest.fixture()
def given_orders(monkeypatch):
    """Replace the data source so tests describe behavior, not sample data."""

    def _given(orders):
        monkeypatch.setattr(orders_service, "load_orders", lambda: list(orders))

    return _given


def get_at_risk(client):
    response = client.get("/api/orders/at-risk")
    assert response.status_code == 200
    return response.get_json()


def test_active_order_above_threshold_is_included(client, given_orders):
    given_orders([make_order("FE-1", estimated_delay_minutes=18)])
    assert [o["order_id"] for o in get_at_risk(client)] == ["FE-1"]


def test_active_order_at_ten_minute_threshold_is_included(client, given_orders):
    given_orders([make_order("FE-1", estimated_delay_minutes=10)])
    assert [o["order_id"] for o in get_at_risk(client)] == ["FE-1"]


def test_active_order_below_threshold_is_excluded(client, given_orders):
    given_orders([make_order("FE-1", estimated_delay_minutes=9)])
    assert get_at_risk(client) == []


def test_delivered_order_with_large_delay_is_excluded(client, given_orders):
    given_orders([make_order("FE-1", status="DELIVERED", estimated_delay_minutes=25)])
    assert get_at_risk(client) == []


def test_cancelled_order_with_large_delay_is_excluded(client, given_orders):
    given_orders([make_order("FE-1", status="CANCELLED", estimated_delay_minutes=21)])
    assert get_at_risk(client) == []


def test_unknown_delay_is_excluded(client, given_orders):
    given_orders([make_order("FE-1", estimated_delay_minutes=None, current_eta=None)])
    assert get_at_risk(client) == []


def test_order_running_early_is_excluded(client, given_orders):
    given_orders([make_order("FE-1", estimated_delay_minutes=-3)])
    assert get_at_risk(client) == []


def test_orders_are_sorted_by_delay_descending(client, given_orders):
    given_orders(
        [
            make_order("FE-LOW", estimated_delay_minutes=10),
            make_order("FE-HIGH", estimated_delay_minutes=30),
            make_order("FE-MID", estimated_delay_minutes=17),
        ]
    )
    assert [o["order_id"] for o in get_at_risk(client)] == [
        "FE-HIGH",
        "FE-MID",
        "FE-LOW",
    ]


def test_equal_delays_keep_source_order(client, given_orders):
    given_orders(
        [
            make_order("FE-FIRST", estimated_delay_minutes=12),
            make_order("FE-SECOND", estimated_delay_minutes=12),
        ]
    )
    assert [o["order_id"] for o in get_at_risk(client)] == ["FE-FIRST", "FE-SECOND"]


def test_no_risky_orders_returns_empty_list(client, given_orders):
    given_orders([make_order("FE-1", estimated_delay_minutes=2)])
    assert get_at_risk(client) == []


def test_response_does_not_add_invented_fields(client, given_orders):
    source = make_order("FE-1", estimated_delay_minutes=18)
    given_orders([source])
    (returned,) = get_at_risk(client)
    assert returned == source


def test_at_risk_path_is_not_treated_as_an_order_id(client, given_orders):
    """The static route must win over /api/orders/<order_id>."""
    given_orders([make_order("FE-1", estimated_delay_minutes=18)])
    payload = client.get("/api/orders/at-risk").get_json()
    assert isinstance(payload, list)
    assert payload != {"error": "order_not_found"}
