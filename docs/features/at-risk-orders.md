# At-Risk Orders Queue

## User

Operations Manager monitoring active food deliveries during a busy service period.

## Goal

Quickly identify active orders that require review, see which need attention first, and inspect an order using the existing order-detail capability.

## Acceptance criteria

1. The queue contains only orders for which the existing `backend/services/risk.py` function `is_at_risk(order)` returns `True`. The queue reuses that function rather than implementing a separate definition of risk.
2. Under the existing rule, an order qualifies only when `status == "ACTIVE"` and `estimated_delay_minutes >= 10`. Exactly 10 minutes qualifies. An unknown delay (`null`) does not qualify. Delivered and cancelled orders do not qualify, regardless of their estimated delay.
3. The queue puts the most urgent qualifying orders first. The precise measure of urgency and the tie breaker require a product decision before this criterion can be tested fully; see Open questions.
4. Each queue item shows enough existing order information for the manager to choose what to inspect next. The exact fields require a product decision; see Open questions.
5. Selecting a queue item uses the existing `GET /api/orders/<order_id>` order-detail capability. The current frontend only alerts the detail URL, so the desired detail presentation remains an open question.
6. When no orders qualify, the frontend shows a useful empty state instead of an empty list without explanation.
7. The frontend obtains order data through a backend API. It does not read `backend/data/orders.json` directly or duplicate the `is_at_risk(order)` business rule.
8. Existing `GET /api/orders` and `GET /api/orders/<order_id>` response contracts remain stable. The queue does not add or depend on a `risk_score` field.

## Out of scope

- Driver reassignment, refunds, maps, and predictive-model changes.
- Changing the existing `is_at_risk(order)` threshold or treatment of unknown delay.
- Introducing a database or live order feed for this MVP.

## Open questions

- What defines “most urgent”: estimated delay descending, another existing field, or an agreed combination? How should ties be ordered?
- Which existing order fields must appear in each queue item?
- How should selecting an order present its details in the frontend while reusing the existing detail API?
- Should the queue refresh automatically or only when the page is loaded or manually refreshed?
- Should the queue have a dedicated API endpoint, or should an existing endpoint gain an optional filter while preserving its current default response?
