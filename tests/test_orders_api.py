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


def test_at_risk_orders_endpoint_returns_only_active_at_risk_sorted(client):
    response = client.get("/api/orders/at-risk")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload) == 3
    # Verify exact IDs and descending delay order
    assert [o["order_id"] for o in payload] == ["FE-48291", "FE-48293", "FE-48297"]
    assert [o["estimated_delay_minutes"] for o in payload] == [18, 14, 10]


def test_at_risk_orders_endpoint_excludes_delivered_cancelled_and_null_delay(client):
    response = client.get("/api/orders/at-risk")
    assert response.status_code == 200
    payload = response.get_json()
    returned_ids = {o["order_id"] for o in payload}
    # FE-48294 (DELIVERED, 19m delay)
    assert "FE-48294" not in returned_ids
    # FE-48296 (CANCELLED, 21m delay)
    assert "FE-48296" not in returned_ids
    # FE-48295 (ACTIVE, null delay)
    assert "FE-48295" not in returned_ids
    # FE-48292 (ACTIVE, 6m delay - below threshold)
    assert "FE-48292" not in returned_ids
    # FE-48298 (ACTIVE, -3m delay)
    assert "FE-48298" not in returned_ids


def test_order_detail_returns_all_expected_fields(client):
    response = client.get("/api/orders/FE-48291")
    assert response.status_code == 200
    payload = response.get_json()
    expected_fields = {
        "order_id",
        "status",
        "promised_eta",
        "current_eta",
        "estimated_delay_minutes",
        "restaurant_status",
        "driver_status",
        "support_opened",
        "previous_intervention",
    }
    assert expected_fields.issubset(payload.keys())

