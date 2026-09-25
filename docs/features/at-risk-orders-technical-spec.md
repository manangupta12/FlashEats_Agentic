# Technical Spec — At-Risk Orders Queue

**Status:** Implementation blueprint.  
**Product requirements:** [at-risk-orders-functional-spec.md](at-risk-orders-functional-spec.md)  
**Architecture:** [../architecture.md](../architecture.md)

## Data flow

```text
Browser (At-Risk queue section)
  → GET /api/at-risk-orders
  → backend/api.py route
  → get_at_risk_orders() in service layer
  → is_at_risk() + sort by estimated_delay_minutes desc
  → load_orders() → backend/data/orders.json
```

Selecting a queue row continues to use existing `GET /api/orders/<order_id>` and the current detail UI interaction (alert to detail URL).

## API contract

### `GET /api/at-risk-orders`

- **200** — JSON array of order objects that pass `is_at_risk`, sorted by `estimated_delay_minutes` descending.
- Empty result — `200` with `[]`.
- Each object uses the same fields as list/detail responses. Do **not** add `risk_score` or other new fields.
- Path is `/api/at-risk-orders` (not `/api/orders/at-risk`) to avoid colliding with `/api/orders/<order_id>`.

### Unchanged

- `GET /api/orders` — full list, existing shape and behavior.
- `GET /api/orders/<order_id>` — detail or `404` with `{"error": "order_not_found"}`.

## Service design

Add a service helper (preferred location: `backend/services/orders.py` or a small dedicated module imported by the API):

```text
get_at_risk_orders() -> list[dict]
  1. load_orders()
  2. filter with is_at_risk(order)
  3. sort by estimated_delay_minutes descending
  4. return list
```

Rules:

- Call `backend.services.risk.is_at_risk`; do not duplicate the threshold or ACTIVE check in the route or frontend.
- Do not mutate the source JSON file.
- Sorting key is `estimated_delay_minutes` (always an int for at-risk orders by definition of the rule).

## Frontend

- Add an **At-Risk Orders** section in `frontend/index.html`.
- Load via `fetch("/api/at-risk-orders")` in `frontend/app.js`.
- Render queue cards with the same row fields as today: order id, status, promised ETA, delay text.
- On click: reuse existing detail behavior (`alert` pointing at `/api/orders/<order_id>`).
- Empty state when the array length is 0 (clear ops-facing message).
- Do not read `orders.json` from the browser.

## Files to change

| File | Change |
|------|--------|
| `backend/services/orders.py` (or new service module) | `get_at_risk_orders()` |
| `backend/api.py` | Register `GET /api/at-risk-orders` |
| `frontend/index.html` | At-risk section markup |
| `frontend/app.js` | Fetch, render, empty state, click handlers |
| `frontend/styles.css` | Minimal styles for the new section if needed |
| `tests/` | New tests for at-risk API (and service if warranted) |

## Test plan

- At-risk endpoint returns only orders matching `is_at_risk`.
- With seed data, order ids are `["FE-48291", "FE-48293", "FE-48297"]` in that order.
- Response items do not include `risk_score`.
- Existing tests in `tests/test_orders_api.py` and `tests/test_risk.py` remain green.
- Empty list is a valid 200 response (unit-level filter/sort coverage can use fixtures if needed).

## Explicit non-changes

- No database, Redis, message queue, or frontend framework.
- No rewrite of `is_at_risk`.
- No driver reassignment, refunds, maps, or predictive scoring.
- Prefer the smallest change that fits the current Flask + vanilla JS + JSON architecture.
