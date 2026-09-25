import json


def test_orders_endpoint_returns_fixture_orders(client, orders_data):
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert response.get_json() == orders_data


def test_order_detail_returns_404_for_unknown_order(client):
    response = client.get("/api/orders/order-missing")
    assert response.status_code == 404
    assert response.get_json() == {"error": "order_not_found"}


def test_at_risk_orders_only_include_matching_orders_in_delay_order(client):
    response = client.get("/api/orders/at-risk")

    assert response.status_code == 200
    payload = response.get_json()
    assert [order["order_id"] for order in payload] == [
        "order-high",
        "order-threshold",
    ]
    assert [order["estimated_delay_minutes"] for order in payload] == [20, 10]


def test_at_risk_orders_use_rule_and_keep_existing_payload_shape(
    client, monkeypatch, tmp_path
):
    fixture_path = tmp_path / "orders.json"
    qualifying = {
        "order_id": "FE-MATCH",
        "status": "ACTIVE",
        "estimated_delay_minutes": 10,
        "promised_eta": "20:00",
        "custom_field": "retained",
    }

    fixture_path.write_text(
        json.dumps(
            [
                {**qualifying, "order_id": "FE-TOP", "estimated_delay_minutes": 18},
                qualifying,
                {**qualifying, "order_id": "FE-TIE", "estimated_delay_minutes": 10},
                {**qualifying, "order_id": "FE-LOW", "estimated_delay_minutes": 6},
                {**qualifying, "order_id": "FE-UNKNOWN", "estimated_delay_minutes": None},
                {"order_id": "FE-MISSING-DELAY", "status": "ACTIVE"},
                {**qualifying, "order_id": "FE-DONE", "status": "DELIVERED", "estimated_delay_minutes": 20},
                {**qualifying, "order_id": "FE-CANCELLED", "status": "CANCELLED", "estimated_delay_minutes": 20},
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("backend.services.orders._DATA_PATH", fixture_path)

    response = client.get("/api/orders/at-risk")

    assert response.status_code == 200
    payload = response.get_json()
    assert [order["order_id"] for order in payload] == [
        "FE-TOP",
        "FE-MATCH",
        "FE-TIE",
    ]
    assert payload[1] == qualifying


def test_at_risk_orders_returns_empty_array_when_none_qualify(client, monkeypatch, tmp_path):
    fixture_path = tmp_path / "orders.json"
    fixture_path.write_text(
        '[{"order_id": "FE-NOT-RISK", "status": "ACTIVE", "estimated_delay_minutes": 8}]',
        encoding="utf-8",
    )
    monkeypatch.setattr("backend.services.orders._DATA_PATH", fixture_path)

    response = client.get("/api/orders/at-risk")

    assert response.status_code == 200
    assert response.get_json() == []


def test_existing_api_does_not_expose_risk_score_field(client, orders_data):
    response = client.get(f"/api/orders/{orders_data[0]['order_id']}")
    assert response.status_code == 200
    payload = response.get_json()
    assert "risk_score" not in payload
    assert "estimated_delay_minutes" in payload
