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
    """Return actionable at-risk orders, most delayed first."""
    return sorted(
        (order for order in load_orders() if is_at_risk(order)),
        key=lambda order: order["estimated_delay_minutes"],
        reverse=True,
    )
