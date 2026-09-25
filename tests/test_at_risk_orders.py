from backend.services.orders import get_at_risk_orders
from backend.services.risk import is_at_risk


def test_at_risk_endpoint_returns_only_at_risk_orders_sorted_by_delay(client):
    response = client.get("/api/at-risk-orders")
    assert response.status_code == 200
    payload = response.get_json()

    assert [order["order_id"] for order in payload] == [
        "FE-48291",
        "FE-48293",
        "FE-48297",
    ]
    assert [order["estimated_delay_minutes"] for order in payload] == [18, 14, 10]
    assert all(is_at_risk(order) for order in payload)


def test_at_risk_endpoint_does_not_expose_risk_score(client):
    response = client.get("/api/at-risk-orders")
    assert response.status_code == 200
    for order in response.get_json():
        assert "risk_score" not in order
        assert "estimated_delay_minutes" in order


def test_get_at_risk_orders_matches_seed_expectation():
    orders = get_at_risk_orders()
    assert [order["order_id"] for order in orders] == [
        "FE-48291",
        "FE-48293",
        "FE-48297",
    ]
