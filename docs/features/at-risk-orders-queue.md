# Spec — At-Risk Orders Queue

## User

Operations Manager monitoring live deliveries during a busy service period.

## Goal

Quickly identify active orders that require intervention now, in priority order.

## Acceptance criteria

1. The queue contains exactly the orders for which `is_at_risk(order)` is true — `status == "ACTIVE"` and `estimated_delay_minutes >= 10`. The rule is not re-implemented; callers reuse `backend/services/risk.py::is_at_risk`. Orders with unknown delay never appear.
2. The queue is sorted by `estimated_delay_minutes` descending (most delayed first), with `order_id` as a deterministic tie-breaker.
3. Each queue item shows enough to triage: `order_id`, `estimated_delay_minutes`, `promised_eta`, `restaurant_status`, `driver_status`.
4. Filtering happens server-side so the business rule stays in one place. The frontend consumes a backend endpoint and never reads `orders.json` or re-implements the rule in JS.
5. Selecting an order uses the existing `GET /api/orders/<order_id>` capability.
6. When no orders qualify, the UI shows an explicit empty state.
7. Existing contracts are unchanged: `GET /api/orders` and `GET /api/orders/<id>` return the same response shapes as today; no new fields (e.g. `risk_score`) are added.
8. Tests cover filtering (non-active and unknown-delay orders excluded), sort order, the empty case, and the new endpoint's contract.

## Out of scope

- Driver reassignment, refunds, maps, predictive-model changes.
- Changing the risk rule itself (threshold stays 10 minutes).
- Changes to existing endpoint response shapes.
- A database, frontend framework, queue infrastructure, or new services.

## Open questions

1. Endpoint shape: new route `GET /api/orders/at-risk` vs. a query param on the existing route (`GET /api/orders?at_risk=true`). Both keep current contracts stable; a separate route is simpler to consume.
2. What "selecting an order" does in the UI — keep the existing alert behavior, or render the fetched order detail inline?
3. Does the queue replace the current order list on the home page, or appear as a separate section/view alongside it?
