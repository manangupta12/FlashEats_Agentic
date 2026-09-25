# Minimal Implementation Plan: At-Risk Orders Queue

This implementation plan adheres strictly to the constraints outlined in `AGENT_TASK.md`, `docs/architecture.md`, `specs.md`, and operational directives.

## Core Constraints Checklist
- [x] **Preserve existing architecture**: Monolithic Flask + static Vanilla HTML/JS. No React, databases, or microservices.
- [x] **Reuse existing risk business logic**: Centralized call to `is_at_risk(order)` in `backend/services/risk.py`.
- [x] **Do not invent new APIs or fields**: Preserve `Order` schema fields without injecting synthetic fields (e.g. `risk_score`).
- [x] **No framework/service rewrite**: Minimal localized additions.
- [x] **Independently verifiable tasks**: Each step has a dedicated test execution command.
- [x] **No code changes yet**: Plan creation only.

---

## Minimal Step-by-Step Execution Tasks

### Task 1: Extend Order Service with `get_at_risk_orders()`
* **Target File**: `backend/services/orders.py`
* **Changes**:
  * Import `is_at_risk` from `backend.services.risk`.
  * Add `get_at_risk_orders() -> list[dict]`:
    * Filter loaded orders via `load_orders()` using `is_at_risk(order)`.
    * Sort filtered list by `estimated_delay_minutes` descending (primary urgency) and `promised_eta` ascending (secondary).
* **Independent Verification**: `python -m pytest tests/test_risk.py`

---

### Task 2: Add Service Layer Unit Tests
* **Target File**: `tests/test_risk.py`
* **Changes**:
  * Add `test_get_at_risk_orders_filters_and_sorts_correctly()`:
    * Verifies only active orders with delay >= 10 are returned.
    * Verifies orders are sorted by delay descending (18m -> 14m -> 10m).
    * Verifies `DELIVERED`, `CANCELLED`, and `null` delay orders are excluded.
* **Independent Verification**: `python -m pytest tests/test_risk.py`

---

### Task 3: Expose `GET /api/orders/at-risk` Route
* **Target File**: `backend/api.py`
* **Changes**:
  * Import `get_at_risk_orders` from `backend.services.orders`.
  * Add route `@app.get("/api/orders/at-risk")` returning `jsonify(get_at_risk_orders())`.
  * Keep existing `@app.get("/api/orders")` untouched to preserve existing contracts.
* **Independent Verification**: `python -m pytest tests/test_orders_api.py`

---

### Task 4: Add Endpoint Integration Tests
* **Target File**: `tests/test_orders_api.py`
* **Changes**:
  * Add `test_at_risk_orders_endpoint_returns_sorted_queue()`:
    * Asserts HTTP status `200 OK`.
    * Asserts response length is 3 for sample dataset (`FE-48291`, `FE-48293`, `FE-48297`).
    * Asserts `risk_score` is NOT present in returned JSON payload.
* **Independent Verification**: `python -m pytest -q`

---

### Task 5: Frontend At-Risk Queue & Empty State UI
* **Target Files**: `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`
* **Changes**:
  * `index.html`: Add section container for the At-Risk Queue and header badge count.
  * `app.js`: Fetch `/api/orders/at-risk` and render order cards with key operational metadata (Order ID, Status, Promised ETA, Delay badge, Restaurant Status, Driver Status, Support Ticket indicator). Render empty state message *"No active orders currently at risk. All live deliveries are operating within normal parameters."* when list is empty. Maintain click listener to view order detail `/api/orders/<order_id>`.
  * `styles.css`: Add styling for risk cards, badges, and empty state layout.
* **Independent Verification**: `python app.py` and run `python -m pytest -q`.

---

## Summary of Verification Commands

1. Unit tests: `python -m pytest tests/test_risk.py`
2. Integration tests: `python -m pytest tests/test_orders_api.py`
3. Full test suite: `python -m pytest -q`
