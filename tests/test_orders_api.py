import json


def test_orders_endpoint_returns_test_orders(client, orders_data):
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert response.get_json() == orders_data


def test_order_detail_returns_404_for_unknown_order(client):
    response = client.get("/api/orders/missing-order")
    assert response.status_code == 404
    assert response.get_json() == {"error": "order_not_found"}


def test_at_risk_orders_are_filtered_and_sorted_by_delay(client):
    response = client.get("/api/orders/at-risk")

    assert response.status_code == 200
    payload = response.get_json()
    assert [order["order_id"] for order in payload] == [
        "order-high",
        "order-threshold",
    ]
    assert [order["estimated_delay_minutes"] for order in payload] == [20, 10]


def test_at_risk_endpoint_applies_every_business_rule_and_preserves_payload(
    client, monkeypatch, tmp_path
):
    data_path = tmp_path / "orders.json"
    matching_order = {
        "order_id": "FE-MATCH",
        "status": "ACTIVE",
        "estimated_delay_minutes": 10,
        "promised_eta": "20:00",
        "custom_field": "preserved",
    }
    data_path.write_text(
        json.dumps(
            [
            {**matching_order, "order_id": "FE-HIGH", "estimated_delay_minutes": 20},
            matching_order,
            {**matching_order, "order_id": "FE-TIE", "estimated_delay_minutes": 10},
            {**matching_order, "order_id": "FE-LOW", "estimated_delay_minutes": 9},
            {**matching_order, "order_id": "FE-UNKNOWN", "estimated_delay_minutes": None},
            {"order_id": "FE-MISSING", "status": "ACTIVE"},
            {**matching_order, "order_id": "FE-DELIVERED", "status": "DELIVERED", "estimated_delay_minutes": 30},
            {**matching_order, "order_id": "FE-CANCELLED", "status": "CANCELLED", "estimated_delay_minutes": 40},
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("backend.services.orders._DATA_PATH", data_path)

    response = client.get("/api/orders/at-risk")

    assert response.status_code == 200
    payload = response.get_json()
    assert [order["order_id"] for order in payload] == [
        "FE-HIGH",
        "FE-MATCH",
        "FE-TIE",
    ]
    assert payload[1] == matching_order


def test_at_risk_orders_return_empty_array_when_no_order_matches(client, monkeypatch, tmp_path):
    data_path = tmp_path / "orders.json"
    data_path.write_text(
        '[{"order_id": "FE-EMPTY", "status": "ACTIVE", '
        '"estimated_delay_minutes": 9}]',
        encoding="utf-8",
    )

    monkeypatch.setattr("backend.services.orders._DATA_PATH", data_path)
    response = client.get("/api/orders/at-risk")

    assert response.status_code == 200
    assert response.get_json() == []


def test_existing_api_does_not_expose_risk_score_field(client, orders_data):
    response = client.get(f"/api/orders/{orders_data[0]['order_id']}")
    assert response.status_code == 200
    payload = response.get_json()
    assert "risk_score" not in payload
    assert "estimated_delay_minutes" in payload
