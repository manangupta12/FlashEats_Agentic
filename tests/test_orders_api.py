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
    response = client.get("/api/orders/at-risk")
    assert response.status_code == 200
    payload = response.get_json()
    
    # Fetch all orders to verify against the complete dataset dynamically
    all_orders_response = client.get("/api/orders")
    all_orders = all_orders_response.get_json()
    
    # 1. Verify active risky orders are included, completed/cancelled/unknown are excluded
    # We do this by ensuring every item in the payload meets the strict criteria.
    for order in payload:
        assert order["status"] == "ACTIVE"
        assert order["estimated_delay_minutes"] is not None
        assert order["estimated_delay_minutes"] >= 10
        
    # 2. Verify we didn't miss any orders that SHOULD be in the list
    expected_count = sum(
        1 for o in all_orders 
        if o["status"] == "ACTIVE" 
        and o.get("estimated_delay_minutes") is not None 
        and o["estimated_delay_minutes"] >= 10
    )
    assert len(payload) == expected_count, "An at-risk order was incorrectly excluded."
    
    # 3. Verify exactly 10 is included if it exists in the original data
    has_exactly_10_in_source = any(
        o["estimated_delay_minutes"] == 10 for o in all_orders if o["status"] == "ACTIVE"
    )
    if has_exactly_10_in_source:
        assert any(o["estimated_delay_minutes"] == 10 for o in payload), "Orders with exactly 10 min delay were incorrectly excluded."

    # 4. Verify results are sorted by estimated_delay_minutes descending
    delays = [order["estimated_delay_minutes"] for order in payload]
    assert delays == sorted(delays, reverse=True), "Orders are not sorted in descending order of delay."
