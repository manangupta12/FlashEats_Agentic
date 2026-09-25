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


def test_at_risk_orders_endpoint(client):
    response = client.get("/api/at-risk-orders")
    assert response.status_code == 200
    payload = response.get_json()

    returned_ids = [order["order_id"] for order in payload]

    # Expected IDs based on backend/data/orders.json
    # FE-48291: ACTIVE, 18 min
    # FE-48293: ACTIVE, 14 min
    # FE-48297: ACTIVE, 10 min (delay exactly 10 included)
    expected_ids = ["FE-48291", "FE-48293", "FE-48297"]

    # Verify results sorted by estimated_delay_minutes descending (18 -> 14 -> 10)
    assert returned_ids == expected_ids

    # Explicit checks to prove exclusions:
    # completed/cancelled excluded
    assert "FE-48294" not in returned_ids  # DELIVERED (delay 19)
    assert "FE-48296" not in returned_ids  # CANCELLED (delay 21)

    # unknown delay excluded
    assert "FE-48295" not in returned_ids  # ACTIVE (delay null)
