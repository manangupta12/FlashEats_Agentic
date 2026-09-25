# Implementation Plan — At-Risk Orders Queue

Spec: `at-risk-orders-queue.md`. Smallest change that fits `docs/architecture.md`.

## Decisions (resolving the spec's open questions)

- **Endpoint**: new route `GET /api/orders/at-risk`. Simpler than a query param; existing contract untouched.
- **Page layout**: queue is a new section above the existing order list. Additive change — the "list all orders" capability stays.
- **Order selection**: keeps the existing click behavior (alert pointing at `GET /api/orders/<id>`). That *is* the existing order-detail capability; building an inline detail panel is out of scope for MVP.

## Step 1 — Queue logic in `backend/services/risk.py`

Add `at_risk_orders(orders) -> list`: filter with `is_at_risk`, sort by `estimated_delay_minutes` descending, `order_id` ascending as tie-break. Lives next to the rule it applies. (~4 lines.)

Tests first in `tests/test_risk.py`:
- non-ACTIVE and `None`-delay orders are excluded
- output is sorted by delay descending
- ties break on `order_id`
- empty input returns empty list

## Step 2 — Route in `backend/api.py`

`GET /api/orders/at-risk` → `jsonify(at_risk_orders(load_orders()))`.

Test in `tests/test_orders_api.py`:
- returns exactly the 3 qualifying fixture orders in order FE-48291 (18) → FE-48293 (14) → FE-48297 (10)
- existing API tests still pass unchanged

## Step 3 — Frontend (`index.html`, `app.js`, `styles.css`)

- `index.html`: add an "At-Risk Queue" section with its own container and an empty-state element.
- `app.js`: extend `orderCard` to also render `restaurant_status` and `driver_status` (spec's required triage fields — shared renderer, both lists benefit); add `loadAtRiskOrders()` that fetches the new endpoint, renders cards, and shows the empty state when the list is empty; reuse the existing click handler.
- `styles.css`: reuse `.order-card`; add a section-heading style only if the markup needs it.

## Step 4 — Verify

- `pytest -q` green (new + existing).
- Smoke: `python app.py` → queue section shows 3 orders sorted 18 → 14 → 10 min; order list below unchanged.
- Empty state is covered by the unit test (no easy way to trigger it with fixture data in the UI).
