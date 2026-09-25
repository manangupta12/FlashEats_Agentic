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


def build_at_risk_queue(orders: list[dict]) -> list[dict]:
    """Return at-risk orders, most urgent first.

    Urgency is largest estimated delay first; ties go to the earliest
    promised ETA, then order_id. promised_eta is compared as text, which
    assumes zero-padded "HH:MM" values within the same service day.
    """
    at_risk = [order for order in orders if is_at_risk(order)]
    return sorted(
        at_risk,
        key=lambda order: (
            -order["estimated_delay_minutes"],
            order["promised_eta"],
            order["order_id"],
        ),
    )
