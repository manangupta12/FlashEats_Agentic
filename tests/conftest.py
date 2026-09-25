import json

import pytest

from backend.api import create_app


@pytest.fixture()
def orders_data():
    return [
        {
            "order_id": "order-high",
            "status": "ACTIVE",
            "estimated_delay_minutes": 20,
            "promised_eta": "20:00",
        },
        {
            "order_id": "order-low",
            "status": "ACTIVE",
            "estimated_delay_minutes": 9,
            "promised_eta": "20:05",
        },
        {
            "order_id": "order-threshold",
            "status": "ACTIVE",
            "estimated_delay_minutes": 10,
            "promised_eta": "20:10",
        },
    ]


@pytest.fixture()
def client(monkeypatch, tmp_path, orders_data):
    fixture_path = tmp_path / "orders.json"
    fixture_path.write_text(json.dumps(orders_data), encoding="utf-8")
    monkeypatch.setattr("backend.services.orders._DATA_PATH", fixture_path)

    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()
