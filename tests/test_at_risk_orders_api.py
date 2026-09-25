def test_at_risk_orders_returns_queue_most_urgent_first(client):
    response = client.get("/api/at-risk-orders")
    assert response.status_code == 200
    payload = response.get_json()
    assert [order["order_id"] for order in payload] == [
        "FE-48291",
        "FE-48293",
        "FE-48297",
    ]


def test_at_risk_orders_do_not_expose_risk_score_field(client):
    payload = client.get("/api/at-risk-orders").get_json()
    assert payload
    for order in payload:
        assert "risk_score" not in order
        assert "estimated_delay_minutes" in order


def test_at_risk_orders_returns_empty_list_when_nothing_at_risk(client, monkeypatch):
    monkeypatch.setattr("backend.api.load_orders", lambda: [])
    response = client.get("/api/at-risk-orders")
    assert response.status_code == 200
    assert response.get_json() == []
