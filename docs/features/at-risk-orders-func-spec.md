# Feature Spec — At-Risk Orders Queue

Source request: [`at-risk-orders-starter.md`](at-risk-orders-starter.md)
Status: Draft — pending answers to Open questions

## User

Operations Manager monitoring live deliveries during a busy service period (internal tool, not customer-facing).

## Goal

Let the Operations Manager quickly see which **active** orders need intervention now, most urgent first, and open any of them using the existing order-detail capability.

"At risk" means exactly the existing business rule `is_at_risk(order)` in `backend/services/risk.py`:

- `status == "ACTIVE"`, and
- `estimated_delay_minutes` is known (not `null`), and
- `estimated_delay_minutes >= 10`.

The README's "delayed / risky" wording is informal and does not define a new rule.

## Acceptance criteria

Items marked *(proposed)* depend on an Open question and are the default unless it is answered otherwise.

### Queue membership

1. The queue contains an order **if and only if** `is_at_risk(order)` returns `True`. The queue logic calls this function; it does not re-implement the rule.
2. Orders with status `DELIVERED` or `CANCELLED` never appear, regardless of delay (e.g. FE-48294 at 19 min, FE-48296 at 21 min).
3. Orders with unknown delay (`estimated_delay_minutes: null`) never appear in the queue and are never shown with an invented numeric delay (e.g. FE-48295).
4. An active order at exactly 10 minutes delay appears (FE-48297). Orders below 10 minutes, including early orders with negative delay, do not (FE-48292 at 6, FE-48298 at −3).
5. With the current `orders.json`, the queue contains exactly FE-48291, FE-48293 and FE-48297.

### Ordering

6. *(proposed — OQ-1)* The queue is sorted by `estimated_delay_minutes` descending; ties are broken by `order_id` ascending so the order is deterministic.
7. With the current data the order is FE-48291 (18), FE-48293 (14), FE-48297 (10).

### API

8. *(proposed — OQ-3)* A new read-only endpoint `GET /api/at-risk-orders` returns `200` with a JSON array of the queued orders, in queue order.
9. Each item uses the existing order fields unchanged. No new computed fields are added; in particular, no `risk_score`.
10. When no orders are at risk, the endpoint returns `200` with `[]`, not a 404 or an error.
11. Existing contracts are unchanged:
    - `GET /api/orders` still returns all 8 orders in file order, and ignores query parameters.
    - `GET /api/orders/<order_id>` still returns the order or `404 {"error": "order_not_found"}`.
    - The detail response still omits `risk_score`.

### UI

12. The browser UI shows the at-risk queue by fetching it from the backend API. It does not read `orders.json` or apply the risk rule in JavaScript.
13. *(proposed — OQ-4)* Each queue entry shows `order_id`, `estimated_delay_minutes`, `promised_eta`, `current_eta`, `restaurant_status`, `driver_status`, `support_opened` and `previous_intervention`. Null values are shown as a readable label such as "Unknown" or "None", never as `null` or `0`.
14. Selecting a queue entry uses the existing `GET /api/orders/<order_id>` endpoint to show that order's details. No new detail endpoint is added.
15. When the queue is empty, the UI shows a clear message such as "No active orders currently need intervention." It does not show a blank area.
16. If the queue request fails, the UI shows an error message, following the existing "Could not load orders" pattern.

### Quality

17. Automated tests cover criteria 1–11: inclusion and exclusion cases, the threshold boundary, unknown delay, ordering and tie-break, the empty result, no `risk_score`, and unchanged existing endpoints.
18. All existing tests in `tests/` keep passing without being modified.
19. `is_at_risk()` and `backend/data/orders.json` are not modified.

## Out of scope

- Driver reassignment, refunds, maps, or any other intervention actions.
- Predictive models, risk scores, or new or changed risk thresholds.
- Changing `is_at_risk()` or recalculating delay from `promised_eta` and `current_eta`. The ETAs have no date or timezone.
- Changes to the existing `/api/orders` or `/api/orders/<order_id>` contracts.
- Databases, caching, queues, background jobs, frontend frameworks, or new services.
- Authentication, live push updates, or auto-refresh.
- Editing or cleaning `orders.json`, for example the mixed `driver_status` values or FE-48296 having a delay but a `null` `current_eta`.

## Open questions

1. **Urgency ordering.** Is "most urgent" simply the largest delay? Should `support_opened: true` or an existing `previous_intervention` move an order up or down? What should break ties? (Proposed: delay descending, then `order_id` ascending.)
2. **Unknown-delay active orders.** FE-48295 has no ETA and no driver (`SEARCHING`). The rule excludes it from the queue. Should the UI also show a separate "delay unknown — needs data" list, without a numeric delay, or should such orders be left out entirely for the MVP? (Proposed: left out of the MVP. Revisit with Operations.)
3. **Endpoint shape.** Should this be a new `GET /api/at-risk-orders`, or a filter on the existing list endpoint? (Decided: new endpoint `GET /api/at-risk-orders`. A filter such as `/api/orders?at_risk=true` would change a parameter that the existing endpoint silently ignores today. A separate path outside `/api/orders/...` can't clash with `/api/orders/<order_id>`.)
4. **Fields shown.** Is the field list in criterion 13 the right amount of information for choosing which order to inspect next?
5. **Page layout.** Should the queue replace the current "Active Orders" list, or appear above it as its own section? (Proposed: its own section above the existing list, which stays unchanged.)
6. **Order-detail display.** Today, selecting an order only shows a `window.alert` with the API URL. Is a simple inline detail panel, filled from `GET /api/orders/<id>`, acceptable as "reusing the existing order-detail capability"?
7. **Runtime version.** The code requires Python 3.10+ (it uses `X | None` type hints), but this isn't documented. Should the README state it as part of this work, or should that be handled separately?
