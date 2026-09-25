import json
from pathlib import Path

from backend.services.risk import is_at_risk


_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "orders.json"


def load_orders() -> list[dict]:
    with _DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


from typing import Optional

def get_order(order_id: str) -> Optional[dict]:
    for order in load_orders():
        if order["order_id"] == order_id:
            return order
    return None


def get_at_risk_orders() -> list[dict]:
    orders = load_orders()
    at_risk = [o for o in orders if is_at_risk(o)]
    at_risk.sort(key=lambda o: o["estimated_delay_minutes"], reverse=True)
    return at_risk
