# Technical Spec — At-Risk Orders Queue

Implementation plan for [at-risk-orders-spec.md](at-risk-orders-spec.md). No code changes yet — this describes what will be built, file by file, before any diff is written.

Constraints carried over from [architecture.md](../architecture.md): no database, no frontend framework, no queue, no new service, no new dependency. Smallest change that fits the existing layers.

## 1. Backend: filtering + sorting

**File:** `backend/services/risk.py`

Add one function alongside `is_at_risk`:

```
get_at_risk_orders(orders: list[dict]) -> list[dict]
```

- Filters `orders` using the existing `is_at_risk(order)` — no new or duplicated risk logic.
- Sorts the filtered list by `estimated_delay_minutes` descending (highest delay = most urgent = first).
- Takes `orders` as a parameter (not a direct file read) so it stays testable without I/O and doesn't duplicate `load_orders()`.

This keeps risk logic and ordering logic centralized in `risk.py`, matching the existing docstring instruction ("keep this rule centralized").

## 2. Backend: API route

**File:** `backend/api.py`

Add:

```
GET /api/at-risk-orders
```

- Calls `load_orders()` then `get_at_risk_orders(...)`, returns the result as JSON (same shape as existing order objects — no new fields, no `risk_score`).
- Registered as its own literal path, separate from `/api/orders` and `/api/orders/<order_id>` — it does not nest under `/api/orders/`, so there is no route-ordering conflict with `/api/orders/<order_id>` to worry about. Confirmed by the passing route tests (see §4).
- Returns `200` with `[]` when nothing is at risk — no empty-state logic in the backend beyond returning an empty list; the empty state itself is a frontend concern (§3).
- No changes to `/api/orders` or `/api/orders/<id>` — their existing contracts and tests stay untouched.

## 3. Frontend

**Files:** `frontend/app.js`, `frontend/index.html`, `frontend/styles.css`

- `index.html`: add a queue container section above or alongside the existing orders list (e.g. `<section id="at-risk-queue">`), plus a dedicated message element for its empty/error state.
- `app.js`: add a `loadAtRiskQueue()` function, structurally parallel to the existing `loadOrders()`:
  - Fetches `/api/at-risk-orders`.
  - Renders a compact card per order reusing the existing `orderCard`-style rendering approach (order ID, delay, promised/current ETA, restaurant/driver status, support flag) — no new fields invented, only what's already on the order object.
  - If the response array is empty, shows an explicit empty-state message (e.g. "No at-risk orders right now") instead of an empty container.
  - Clicking an entry reuses the same click-through behavior already used for `/api/orders/<id>` (currently an `alert()`; not being upgraded as part of this feature — see open question in the feature spec).
  - Data comes only from `fetch("/api/at-risk-orders")` — no direct JSON file access, no client-side reimplementation of the risk rule.
- `styles.css`: minor styling for the new section/cards, reusing existing class patterns rather than introducing a new visual system.

## 4. Tests

**File:** `tests/test_risk.py`

- `get_at_risk_orders` returns only ACTIVE orders with `estimated_delay_minutes >= 10`.
- Result excludes orders with `estimated_delay_minutes is None`.
- Result excludes DELIVERED and CANCELLED orders even with a high delay.
- Result is sorted descending by delay.
- Empty input list returns an empty list.

**File:** `tests/test_orders_api.py`

- `GET /api/at-risk-orders` returns exactly `["FE-48291", "FE-48293", "FE-48297"]` in that order, against the current fixture data.
- `GET /api/at-risk-orders` items do not contain `risk_score`.
- `GET /api/orders` still returns 8 orders with `FE-48291` first (regression check — confirms the new route didn't shadow or affect the existing one).
- `GET /api/at-risk-orders` returns `200` and `[]` when no order in the data set qualifies (achieved by asserting against a filtered/mocked list, or documenting this as covered indirectly by the unit-level empty-list test in `test_risk.py` if the fixture data can't easily be swapped per-test).

## 5. Non-goals for this change

Matches feature-spec §4 out of scope: no driver reassignment, refunds, maps, predictive scoring, threshold changes, real-time updates, or pagination/filtering beyond the at-risk queue.

## 6. Open technical decision

Tie-breaking for equal delays (feature-spec open question) is not resolved here. Default behavior if unresolved before implementation: stable sort by delay only, so equal-delay orders keep their original `orders.json` relative order (Python's `sorted()` is stable) — this needs confirmation before being treated as final, not just accepted as a side effect of implementation.