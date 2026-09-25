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
def test_at_risk_orders_behavior(mock_load, client):
    mock_load.return_value = [
        {"order_id": "1", "status": "ACTIVE", "estimated_delay_minutes": 15},
        {"order_id": "2", "status": "ACTIVE", "estimated_delay_minutes": 5},
        {"order_id": "3", "status": "DELIVERED", "estimated_delay_minutes": 20},
        {"order_id": "4", "status": "ACTIVE", "estimated_delay_minutes": 10},
        {"order_id": "5", "status": "ACTIVE", "estimated_delay_minutes": None},
    ]

    response = client.get("/api/orders/at-risk")
    assert response.status_code == 200
    payload = response.get_json()

    # Active risky orders (>= 10) are included, non-active or null delay are excluded
    # Sorting should be descending (15, then 10)
    assert len(payload) == 2
    assert payload[0]["order_id"] == "1"
    assert payload[1]["order_id"] == "4"
