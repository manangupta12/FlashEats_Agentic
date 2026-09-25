import json
from pathlib import Path

from backend.services.risk import is_at_risk


_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "orders.json"


def load_orders() -> list[dict]:
    with _DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_order(order_id: str) -> dict | None:
    for order in load_orders():
        if order["order_id"] == order_id:
            return order
    return None


def get_at_risk_orders() -> list[dict]:
    at_risk_orders = [order for order in load_orders() if is_at_risk(order)]
    return sorted(
        at_risk_orders,
        key=lambda order: (
            -(order.get("estimated_delay_minutes") or 0),
            0 if order.get("support_opened") else 1,
            order.get("order_id", ""),
        ),
    )
