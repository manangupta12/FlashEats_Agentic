def is_at_risk(order: dict) -> bool:
    """Return whether an order is operationally at risk.

    Existing business rule used by Operations:
    - only ACTIVE orders are actionable;
    - an order is at risk when estimated delay is at least 10 minutes;
    - if estimated delay is unknown, we do not classify the order as at risk.

    Keep this rule centralized. Callers should reuse it rather than duplicating it.
    """
    delay = order.get("estimated_delay_minutes")
    return (
        order.get("status") == "ACTIVE"
        and delay is not None
        and delay >= 10
    )


def at_risk_orders(orders: list[dict]) -> list[dict]:
    """Qualifying orders, most delayed first; order_id breaks ties."""
    return sorted(
        (order for order in orders if is_at_risk(order)),
        key=lambda order: (-order["estimated_delay_minutes"], order["order_id"]),
    )
