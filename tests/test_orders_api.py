from unittest.mock import patch

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


@patch("backend.api.load_orders")
def test_orders_endpoint_with_risk_filter(mock_load_orders, client):
    mock_load_orders.return_value = [
        {"order_id": "1", "status": "ACTIVE", "estimated_delay_minutes": 15, "promised_eta": "2024-01-01T12:00:00Z"},
        {"order_id": "2", "status": "ACTIVE", "estimated_delay_minutes": 15, "promised_eta": "2024-01-01T11:00:00Z"},
        {"order_id": "3", "status": "DELIVERED", "estimated_delay_minutes": 20, "promised_eta": "2024-01-01T10:00:00Z"},
        {"order_id": "4", "status": "ACTIVE", "estimated_delay_minutes": 5, "promised_eta": "2024-01-01T10:00:00Z"},
    ]
    response = client.get("/api/orders?risk=true")
    assert response.status_code == 200
    payload = response.get_json()
    
    assert len(payload) == 2
    # Verify sorting: highest delay first, then earlier promised_eta
    assert payload[0]["order_id"] == "2"
    assert payload[1]["order_id"] == "1"

@patch("backend.api.load_orders")
def test_orders_endpoint_with_risk_filter_empty_state(mock_load_orders, client):
    mock_load_orders.return_value = [
        {"order_id": "1", "status": "ACTIVE", "estimated_delay_minutes": 5, "promised_eta": "2024-01-01T12:00:00Z"}
    ]
    response = client.get("/api/orders?risk=true")
    assert response.status_code == 200
    payload = response.get_json()
    
    assert payload == []
