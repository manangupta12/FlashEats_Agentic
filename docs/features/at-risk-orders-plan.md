# Implementation Plan — At-Risk Orders Queue

Derived from `at-risk-orders-spec.md` (functional) and `at-risk-orders-tech-spec.md` (technical).
Four tasks, executed and reviewed one at a time. No code is written before this plan is approved.

---

## Task 1 — Backend at-risk endpoint

**Files:** `backend/services/orders.py`, `backend/api.py`

1. In `backend/services/orders.py`:
   - `from backend.services.risk import is_at_risk`
   - add:
     ```python
     def get_at_risk_orders() -> list[dict]:
         at_risk = [o for o in load_orders() if is_at_risk(o)]
         return sorted(at_risk, key=lambda o: o["estimated_delay_minutes"], reverse=True)
     ```
   - Rule is **imported, never re-implemented**. Filter runs before sort, so the sort key
     is never `None`. `sorted` is stable → equal delays keep source order.
2. In `backend/api.py`: add the route under the existing `/api/orders` hierarchy —
   **`/api/orders/at-risk`**, not a new top-level `/api/at-risk-orders` path — thin,
   delegating to the service:
   ```python
   @app.get("/api/orders/at-risk")
   def at_risk_orders():
       return jsonify(get_at_risk_orders())
   ```
   Registered before `/api/orders/<order_id>`; a test asserts the static rule wins.
3. Do not touch `risk.py`, `models.py`, `orders.json`, or the existing two routes.

**Done when:** endpoint returns the filtered, sorted list; existing tests still pass.

---

## Task 2 — Behavioral tests

**File:** `tests/test_at_risk_orders.py` (new)

Cases, each a distinct behavior of the spec:

| # | Behavior | Spec AC |
|---|---|---|
| 1 | Active order above threshold is included | 1 |
| 2 | Active order at exactly 10 min is included | 2 |
| 3 | Active order below threshold (9) is excluded | 1 |
| 4 | `DELIVERED` order with large delay is excluded | 4 |
| 5 | `CANCELLED` order with large delay is excluded | 4 |
| 6 | Active order with `null` delay is excluded | 3 |
| 7 | Active order with negative delay is excluded | 1 |
| 8 | Results sorted by delay descending | 5 |
| 9 | Empty result → `200` with `[]` | spec §6 |
| 10 | Equal delays keep source order (stable sort) | 5 |
| 11 | Response item is byte-for-byte the source order — no invented fields | 8 |
| 12 | `/api/orders/at-risk` is not handled as an order id | 6 |

Style: follow `tests/test_risk.py` — a local `make_order(**overrides)` factory plus a
`given_orders` fixture that substitutes the service-layer data source, so each test
supplies exactly the orders its case needs.

**Tests must not assert against the contents of `backend/data/orders.json`.** Hardcoding
live order ids or delay values there produces tests that describe sample data rather than
behavior: they break whenever the fixture file is edited, and they keep passing when the
rule itself regresses (e.g. a test asserting `"FE-48297" in ids` still passes if that
order's delay is changed to 30, so it no longer proves the 10-minute boundary at all).

**Done when:** new tests pass and the three existing test modules are unchanged and green.

---

## Task 3 — UI queue with loading / empty / error states

**Files:** `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`

1. `index.html`: add an "At-Risk Orders" section above the existing orders list, with its own
   message element and list container. Keep the existing section intact.
2. `app.js`: `loadAtRiskOrders()` mirroring `loadOrders()`:
   - **loading** — message "Loading at-risk orders…" before the fetch resolves;
   - **error** — non-OK response or thrown fetch → "Could not load at-risk orders: …",
     list cleared;
   - **empty** — `[]` → "No orders currently at risk"；
   - **populated** — "N orders at risk" + one card per order; card shows
     `order_id`, `status`, `promised_eta`, `current_eta`, `estimated_delay_minutes`,
     `restaurant_status`, `driver_status` (existing fields only).
   - Render in the order the API returns — **no client-side filtering or re-sorting**.
   - Clicking a card reuses the existing detail path (`/api/orders/<id>`), same as today.
3. `styles.css`: minimal rules for the queue, urgency emphasis on the delay, and state text.
   No framework, no build step.

**Done when:** all four states render correctly against the real server.

---

## Task 4 — Verify against spec, run all tests

1. `pytest -q` — new tests plus all pre-existing tests green.
2. `python app.py`, open `http://127.0.0.1:5000`, check
   `GET /api/orders/at-risk` returns `FE-48291 (18)`, `FE-48293 (14)`, `FE-48297 (10)`,
   in that order, and that the UI matches.
3. Walk the functional spec's acceptance criteria 1–11 and record pass/fail for each.
4. Confirm untouched: `risk.py`, `models.py`, `orders.json`, existing tests, existing routes.
5. Re-check the open questions; leave them open rather than deciding them silently.

---

## Sequencing & review gates

Task 1 → review diff → Task 2 → run tests → Task 3 → review diff → Task 4.
Stop after each task. Nothing outside the listed files is edited.
