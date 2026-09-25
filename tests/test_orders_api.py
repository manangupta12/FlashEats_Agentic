def test_orders_endpoint_returns_existing_orders(client):
    response = client.get("/api/orders")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 8
    assert payload[0]["order_id"] == "FE-48291"


def test_order_detail_returns_404_for_unknown_order(client):
    response = client.get("/api/orders/FE-DOES-NOT-EXIST")
    assert response.status_code == 404
    assert response.get_json() == {"error": "order_not_found"}


def test_existing_api_does_not_expose_risk_score_field(client):
    response = client.get("/api/orders/FE-48291")
    assert response.status_code == 200
    payload = response.get_json()
    assert "risk_score" not in payload
    assert "estimated_delay_minutes" in payload


def test_at_risk_orders_endpoint_returns_filtered_and_sorted_queue(client):
    response = client.get("/api/orders/at-risk")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 3

    order_ids = [order["order_id"] for order in payload]
    assert order_ids == ["FE-48291", "FE-48293", "FE-48297"]

    delays = [order["estimated_delay_minutes"] for order in payload]
    assert delays == [18, 14, 10]

    for order in payload:
        assert order["status"] == "ACTIVE"
        assert "risk_score" not in order


def test_completed_and_cancelled_orders_excluded_from_at_risk_endpoint(client):
    response = client.get("/api/orders/at-risk")
    payload = response.get_json()
    order_ids = [order["order_id"] for order in payload]
    # FE-48294 is DELIVERED (19m delay) and FE-48296 is CANCELLED (21m delay)
    assert "FE-48294" not in order_ids
    assert "FE-48296" not in order_ids


def test_unknown_delay_orders_excluded_from_at_risk_endpoint(client):
    response = client.get("/api/orders/at-risk")
    payload = response.get_json()
    order_ids = [order["order_id"] for order in payload]
    # FE-48295 is ACTIVE with null estimated_delay_minutes
    assert "FE-48295" not in order_ids


def test_delay_exactly_10_minutes_included_in_at_risk_endpoint(client):
    response = client.get("/api/orders/at-risk")
    payload = response.get_json()
    order_ids = [order["order_id"] for order in payload]
    # FE-48297 is ACTIVE with estimated_delay_minutes == 10
    assert "FE-48297" in order_ids
    target_order = next(o for o in payload if o["order_id"] == "FE-48297")
    assert target_order["estimated_delay_minutes"] == 10


def test_at_risk_endpoint_results_sorted_by_delay_descending(client):
    response = client.get("/api/orders/at-risk")
    payload = response.get_json()
    delays = [order["estimated_delay_minutes"] for order in payload]
    assert delays == sorted(delays, reverse=True)
    assert delays == [18, 14, 10]


