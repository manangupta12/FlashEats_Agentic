from backend.services.risk import at_risk_queue


def make_order(order_id, **overrides):
    order = {
        "order_id": order_id,
        "status": "ACTIVE",
        "promised_eta": "20:00",
        "current_eta": "20:15",
        "estimated_delay_minutes": 15,
        "restaurant_status": "READY",
        "driver_status": "ASSIGNED",
        "support_opened": False,
        "previous_intervention": None,
    }
    order.update(overrides)
    return order


def ids(orders):
    return [order["order_id"] for order in orders]


# --- at_risk_queue: filtering -------------------------------------------------


def test_queue_includes_active_order_at_threshold():
    orders = [make_order("A", estimated_delay_minutes=10)]
    assert ids(at_risk_queue(orders)) == ["A"]


def test_queue_excludes_orders_the_risk_rule_rejects():
    orders = [
        make_order("below", estimated_delay_minutes=9),
        make_order("early", estimated_delay_minutes=-3),
        make_order("unknown", estimated_delay_minutes=None),
        make_order("delivered", status="DELIVERED", estimated_delay_minutes=25),
        make_order("cancelled", status="CANCELLED", estimated_delay_minutes=21),
    ]
    assert at_risk_queue(orders) == []


def test_queue_is_empty_for_empty_input():
    assert at_risk_queue([]) == []


# --- at_risk_queue: ordering --------------------------------------------------


def test_queue_puts_largest_delay_first():
    orders = [
        make_order("A", estimated_delay_minutes=10),
        make_order("B", estimated_delay_minutes=30),
        make_order("C", estimated_delay_minutes=14),
    ]
    assert ids(at_risk_queue(orders)) == ["B", "C", "A"]


def test_queue_breaks_delay_ties_by_earlier_promised_eta():
    orders = [
        make_order("late-promise", estimated_delay_minutes=12, promised_eta="20:30"),
        make_order("early-promise", estimated_delay_minutes=12, promised_eta="19:45"),
    ]
    assert ids(at_risk_queue(orders)) == ["early-promise", "late-promise"]


def test_queue_breaks_full_ties_by_order_id():
    orders = [
        make_order("FE-2", estimated_delay_minutes=12, promised_eta="20:00"),
        make_order("FE-1", estimated_delay_minutes=12, promised_eta="20:00"),
    ]
    assert ids(at_risk_queue(orders)) == ["FE-1", "FE-2"]


# --- at_risk_queue: returned data ---------------------------------------------


def test_queue_returns_orders_unchanged_and_does_not_mutate_input():
    orders = [
        make_order("A", estimated_delay_minutes=10),
        make_order("B", estimated_delay_minutes=20),
    ]
    snapshot = [dict(order) for order in orders]

    result = at_risk_queue(orders)

    assert result == [snapshot[1], snapshot[0]]
    assert orders == snapshot
    assert all("risk_score" not in order for order in result)


# --- GET /api/at-risk-orders ----------------------------------------------------


def test_endpoint_returns_expected_queue_for_seed_data(client):
    response = client.get("/api/at-risk-orders")
    assert response.status_code == 200
    assert ids(response.get_json()) == ["FE-48291", "FE-48293", "FE-48297"]


def test_endpoint_orders_have_same_shape_as_orders_list(client):
    all_orders = {o["order_id"]: o for o in client.get("/api/orders").get_json()}

    for order in client.get("/api/at-risk-orders").get_json():
        assert order.keys() == all_orders[order["order_id"]].keys()
        assert "risk_score" not in order


def test_endpoint_returns_empty_list_when_nothing_is_at_risk(client, monkeypatch):
    # api.py imports load_orders by name, so patch it there.
    monkeypatch.setattr(
        "backend.api.load_orders",
        lambda: [make_order("done", status="DELIVERED", estimated_delay_minutes=40)],
    )
    response = client.get("/api/at-risk-orders")
    assert response.status_code == 200
    assert response.get_json() == []


def test_endpoint_uses_service_ordering(client, monkeypatch):
    monkeypatch.setattr(
        "backend.api.load_orders",
        lambda: [
            make_order("A", estimated_delay_minutes=11),
            make_order("B", estimated_delay_minutes=None),
            make_order("C", estimated_delay_minutes=25),
        ],
    )
    assert ids(client.get("/api/at-risk-orders").get_json()) == ["C", "A"]


def test_existing_endpoints_are_unaffected(client):
    assert len(client.get("/api/orders").get_json()) == 8
    assert client.get("/api/orders/FE-48291").get_json()["order_id"] == "FE-48291"
