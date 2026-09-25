import json


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


def test_existing_order_endpoints_preserve_unfiltered_data(client, monkeypatch, tmp_path):
    orders = [
        {"order_id": "active", "status": "ACTIVE", "estimated_delay_minutes": 10},
        {
            "order_id": "delivered",
            "status": "DELIVERED",
            "estimated_delay_minutes": 25,
            "current_eta": None,
        },
    ]
    data_path = tmp_path / "orders.json"
    data_path.write_text(json.dumps(orders), encoding="utf-8")
    monkeypatch.setattr("backend.services.orders._DATA_PATH", data_path)

    list_response = client.get("/api/orders")
    detail_response = client.get("/api/orders/delivered")

    assert list_response.status_code == 200
    assert list_response.get_json() == orders
    assert detail_response.status_code == 200
    assert detail_response.get_json() == orders[1]


def test_at_risk_orders_endpoint_uses_existing_risk_rule(client, monkeypatch):
    orders = [
        {"order_id": "below", "status": "ACTIVE", "estimated_delay_minutes": 9},
        {"order_id": "threshold", "status": "ACTIVE", "estimated_delay_minutes": 10},
        {"order_id": "unknown", "status": "ACTIVE", "estimated_delay_minutes": None},
        {"order_id": "delivered", "status": "DELIVERED", "estimated_delay_minutes": 25},
        {"order_id": "completed", "status": "COMPLETED", "estimated_delay_minutes": 25},
        {"order_id": "cancelled", "status": "CANCELLED", "estimated_delay_minutes": 25},
        {"order_id": "higher", "status": "ACTIVE", "estimated_delay_minutes": 18},
    ]
    monkeypatch.setattr("backend.api.load_orders", lambda: orders)

    response = client.get("/api/at-risk-orders")

    assert response.status_code == 200
    assert response.get_json() == [orders[6], orders[1]]
    assert "risk_score" not in response.get_json()[0]


def test_at_risk_orders_endpoint_returns_empty_list_when_none_qualify(client, monkeypatch):
    monkeypatch.setattr("backend.api.load_orders", lambda: [])

    response = client.get("/api/at-risk-orders")

    assert response.status_code == 200
    assert response.get_json() == []
