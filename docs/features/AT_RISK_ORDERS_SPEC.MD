# Feature Spec — At-Risk Orders Queue

Refines [at-risk-orders-starter.md](at-risk-orders-starter.md) using the existing repository behaviour documented in [repo-inspection.md](../repo-inspection.md). No implementation details below — this is scope and acceptance only.

## 1. User

Operations Manager, monitoring active deliveries during a busy service period.

## 2. Goal

Quickly identify active orders that need attention right now, most urgent first, without digging through the full order list.

## 3. Acceptance criteria

- The queue includes an order only if it satisfies the existing `is_at_risk` business rule (ACTIVE status, delay known, delay ≥ 10 minutes). No new or looser risk definition is introduced.
- An order with `estimated_delay_minutes` exactly equal to 10 is included (boundary is inclusive, matching current rule and tests).
- An order with `estimated_delay_minutes` of `null` is excluded, and is never treated as having zero or any other numeric delay.
- DELIVERED and CANCELLED orders are excluded regardless of their delay value.
- The queue is ordered with the most urgent order first. Highest `estimated_delay_minutes` first is the agreed ordering rule.
- Each queue entry shows enough information for the Operations Manager to decide whether to inspect the order further (at minimum: order ID, delay, and current status information already present on the order object).
- Selecting a queue entry reuses the existing order-detail capability (`GET /api/orders/<id>`); no new detail data is introduced.
- When no order currently qualifies as at risk, the queue shows a clear empty state instead of an empty or missing list.
- The frontend obtains queue data from a backend API; it does not read `backend/data/orders.json` or recompute the risk rule independently.
- Existing API contracts are unchanged: `/api/orders` still returns all 8 orders in file order, `/api/orders/<id>` still 404s for unknown IDs and still excludes `risk_score`.

## 4. Out of scope

- Driver reassignment.
- Refunds.
- Maps or geolocation display.
- Any predictive-model or risk-scoring changes (no `risk_score`, no probability, no ML).
- Any change to the risk threshold or its inputs.
- Real-time/streaming updates (polling or push).
- Pagination or filtering beyond the at-risk queue itself.

## 5. Open questions

- Tie-breaking when two orders have the same delay: by promised ETA, or by order ID? Not yet confirmed with Operations.
- Should orders with unknown delay (excluded from risk by rule) appear anywhere as a separate "needs review" bucket, or stay fully hidden? Currently assumed fully hidden, per the rule.
- What does "reuse the existing order-detail capability" mean in the UI today — is the current `alert()`-based click-through acceptable, or is a real detail view expected as part of this feature?
- Should the queue auto-refresh, or is a manual reload (consistent with the current orders view) sufficient for MVP?