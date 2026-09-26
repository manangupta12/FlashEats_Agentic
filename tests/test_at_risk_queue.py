from backend.services.risk import at_risk_queue, is_at_risk


def make_order(order_id, **overrides):
    order = {
        "order_id": order_id,
        "status": "ACTIVE",
        "promised_eta": "20:00",
        "current_eta": "20:15",
        "estimated_delay_minutes": 15,
        "restaurant_status": "READY",
        "driver_status": "ASSIGNED",
        "support_opened": False,
        "previous_intervention": None,
    }
    order.update(overrides)
    return order


def queue_ids(orders):
    return [order["order_id"] for order in at_risk_queue(orders)]


# --- at_risk_queue(): membership ---


def test_active_risky_order_is_included():
    assert queue_ids([make_order("A", estimated_delay_minutes=18)]) == ["A"]


def test_delivered_and_cancelled_orders_are_excluded():
    orders = [
        make_order("DELIVERED", status="DELIVERED", estimated_delay_minutes=25),
        make_order("CANCELLED", status="CANCELLED", estimated_delay_minutes=30),
    ]
    assert queue_ids(orders) == []


def test_unknown_delay_is_excluded():
    orders = [make_order("UNKNOWN", estimated_delay_minutes=None, current_eta=None)]
    assert queue_ids(orders) == []


def test_delay_exactly_ten_is_included():
    assert queue_ids([make_order("TEN", estimated_delay_minutes=10)]) == ["TEN"]


def test_delay_below_threshold_and_early_orders_are_excluded():
    orders = [
        make_order("NINE", estimated_delay_minutes=9),
        make_order("EARLY", estimated_delay_minutes=-3),
    ]
    assert queue_ids(orders) == []


def test_membership_matches_is_at_risk_rule():
    orders = [
        make_order("A", estimated_delay_minutes=18),
        make_order("B", estimated_delay_minutes=6),
        make_order("C", status="DELIVERED", estimated_delay_minutes=19),
        make_order("D", estimated_delay_minutes=None),
        make_order("E", estimated_delay_minutes=10),
    ]
    expected = {order["order_id"] for order in orders if is_at_risk(order)}
    assert set(queue_ids(orders)) == expected


# --- at_risk_queue(): ordering ---


def test_results_sorted_by_delay_descending():
    orders = [
        make_order("LOW", estimated_delay_minutes=10),
        make_order("HIGH", estimated_delay_minutes=30),
        make_order("MID", estimated_delay_minutes=14),
    ]
    assert queue_ids(orders) == ["HIGH", "MID", "LOW"]


def test_equal_delays_are_ordered_by_order_id():
    orders = [
        make_order("FE-2", estimated_delay_minutes=12),
        make_order("FE-1", estimated_delay_minutes=12),
    ]
    assert queue_ids(orders) == ["FE-1", "FE-2"]


# --- at_risk_queue(): output shape ---


def test_empty_input_returns_empty_queue():
    assert at_risk_queue([]) == []


def test_orders_are_returned_without_added_fields():
    order = make_order("A", estimated_delay_minutes=18)
    assert at_risk_queue([order]) == [make_order("A", estimated_delay_minutes=18)]


# --- GET /api/at-risk-orders ---


def test_at_risk_endpoint_returns_expected_orders_most_urgent_first(client):
    response = client.get("/api/at-risk-orders")
    assert response.status_code == 200
    payload = response.get_json()
    assert [order["order_id"] for order in payload] == [
        "FE-48291",
        "FE-48293",
        "FE-48297",
    ]
    delays = [order["estimated_delay_minutes"] for order in payload]
    assert delays == sorted(delays, reverse=True)


def test_at_risk_endpoint_excludes_inactive_and_unknown_delay_orders(client):
    ids = {order["order_id"] for order in client.get("/api/at-risk-orders").get_json()}
    assert "FE-48294" not in ids  # DELIVERED, 19 min
    assert "FE-48296" not in ids  # CANCELLED, 21 min
    assert "FE-48295" not in ids  # ACTIVE, unknown delay


def test_at_risk_endpoint_does_not_expose_risk_score_field(client):
    for order in client.get("/api/at-risk-orders").get_json():
        assert "risk_score" not in order


def test_at_risk_endpoint_returns_empty_list_when_nothing_at_risk(client, monkeypatch):
    # api.py imports load_orders by name, so patch it where the route uses it.
    monkeypatch.setattr("backend.api.load_orders", lambda: [])
    response = client.get("/api/at-risk-orders")
    assert response.status_code == 200
    assert response.get_json() == []


# --- existing contracts preserved ---


def test_orders_endpoint_still_returns_all_orders_in_file_order(client):
    payload = client.get("/api/orders").get_json()
    assert len(payload) == 8
    assert [order["order_id"] for order in payload] == [
        "FE-48291",
        "FE-48292",
        "FE-48293",
        "FE-48294",
        "FE-48295",
        "FE-48296",
        "FE-48297",
        "FE-48298",
    ]


def test_order_detail_still_returns_non_risky_orders(client):
    response = client.get("/api/orders/FE-48294")
    assert response.status_code == 200
    assert response.get_json()["status"] == "DELIVERED"


def test_order_detail_still_returns_404_for_unknown_order(client):
    response = client.get("/api/orders/FE-DOES-NOT-EXIST")
    assert response.status_code == 404
    assert response.get_json() == {"error": "order_not_found"}
