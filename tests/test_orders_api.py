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


def test_at_risk_endpoint_applies_rule_and_sorts_by_delay(client, monkeypatch):
    from backend.services import orders as order_service

    records = [
        {"order_id": "late", "status": "ACTIVE", "estimated_delay_minutes": 12},
        {"order_id": "threshold", "status": "ACTIVE", "estimated_delay_minutes": 10},
        {"order_id": "early", "status": "ACTIVE", "estimated_delay_minutes": 9},
        {"order_id": "unknown", "status": "ACTIVE", "estimated_delay_minutes": None},
        {"order_id": "delivered", "status": "DELIVERED", "estimated_delay_minutes": 40},
        {"order_id": "cancelled", "status": "CANCELLED", "estimated_delay_minutes": 40},
    ]
    monkeypatch.setattr(order_service, "load_orders", lambda: records)
    response = client.get("/api/orders/at-risk")
    assert response.status_code == 200
    payload = response.get_json()
    delays = [order["estimated_delay_minutes"] for order in payload]
    assert delays == sorted(delays, reverse=True)
    assert [order["order_id"] for order in payload] == ["late", "threshold"]


def test_at_risk_endpoint_does_not_change_existing_orders_contract(client):
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert len(response.get_json()) == 8
