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


def test_at_risk_orders_endpoint_returns_only_eligible_orders(client):
    response = client.get("/api/orders/at-risk")
    assert response.status_code == 200
    payload = response.get_json()
    assert [order["order_id"] for order in payload] == [
        "FE-48291",
        "FE-48293",
        "FE-48297",
    ]


def test_at_risk_orders_query_param_returns_same_priority_queue(client):
    response = client.get("/api/orders?at_risk=true")
    assert response.status_code == 200
    payload = response.get_json()
    assert [order["order_id"] for order in payload] == [
        "FE-48291",
        "FE-48293",
        "FE-48297",
    ]
