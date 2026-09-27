# Implementation Plan — At-Risk Orders Queue

Implements `docs/features/at-risk-orders-spec.md`. Do one task at a time, review the diff, and run the tests before moving on.

## Task 0 — Baseline

- `python -m pip install -r requirements.txt`. Flask is not currently installed, so `tests/conftest.py` fails on import.
- `pytest -q`. Expect **7 passed** before any change.

## Task 1 — Queue function in the service layer

**File:** `backend/services/risk.py`

Add a pure function next to `is_at_risk`:

```python
def at_risk_queue(orders: list[dict]) -> list[dict]:
    """Return at-risk orders, most urgent first (see spec D1)."""
```

- Filter with `is_at_risk`. Don't copy the threshold or the status check.
- Sort by key `(-estimated_delay_minutes, promised_eta, order_id)`. This is safe because every order that passes the filter has a non-null delay.
- Return the original dicts unchanged, with no added keys.
- It takes `orders` as an argument instead of calling `load_orders()`. This keeps it independent of I/O, easy to test, and inside the `risk.py` boundary.

**Tests:** `tests/test_at_risk_orders.py` (unit section). It uses a local `make_order(order_id, **overrides)` factory.

- Keeps only qualifying orders. Excludes DELIVERED, CANCELLED, `None`, 9 and negative delays.
- Sorts by delay descending.
- Tie on delay: earlier `promised_eta` first, then `order_id`.
- Empty input returns `[]`, and input with nothing qualifying returns `[]`.
- Returned dicts have the same keys as the input (no `risk_score`).

**Verify:** `pytest -q tests/test_at_risk_orders.py -k queue`

## Task 2 — API endpoint

**File:** `backend/api.py`

```python
@app.get("/api/at-risk-orders")
def at_risk_orders():
    return jsonify(at_risk_queue(load_orders()))
```

- Import `at_risk_queue` from `backend.services.risk`.
- Leave the existing routes unchanged.

**Tests:** `tests/test_at_risk_orders.py` (endpoint section).

- Returns `["FE-48291", "FE-48293", "FE-48297"]` in that order (acceptance criteria 1–5).
- No `risk_score` in any element, and each element's keys match the same order in `/api/orders` (criterion 6).
- Empty case returns `200 []` (criterion 7). Use `monkeypatch.setattr("backend.api.load_orders", lambda: [...])`.
  - ⚠️ Patch `backend.api.load_orders`, **not** `backend.services.orders.load_orders`. `api.py` imports the name directly, so patching the source module has no effect on the route.
- `/api/orders` still returns 8 orders (already covered, and must still pass).

**Verify:** `pytest -q`

## Task 3 — Frontend queue section

**Files:** `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`

- `index.html`: add a section above the existing list:
  - a heading
  - `#at-risk-message` for the loading, empty and error text
  - `#at-risk-orders` for the list
  - `#order-detail` for the detail panel
- `app.js`:
  - Add an `escapeHtml()` helper and use it for every value inserted into new markup.
  - `loadAtRiskOrders()` fetches `/api/at-risk-orders` and renders the cards in the order received. Do **not** re-sort or re-filter on the client.
  - Show the empty or error state as in the spec. The error must not stop `loadOrders()` from running.
  - When a card is clicked, `showOrderDetail(id)` fetches `/api/orders/${encodeURIComponent(id)}` and renders the fields in `#order-detail`. Handle 404 and network errors.
  - Leave `orderCard` and `loadOrders` behavior unchanged.
- `styles.css`: small additions for the queue cards, a delay badge and the detail panel, reusing the existing palette.

**Verify manually:** `python app.py`, open http://127.0.0.1:5000

- The queue shows 48291, 48293 and 48297 in that order, above the unchanged list of 8.
- Clicking a card shows its detail.
- Temporarily change the fetch URL to a bad path to check the error state. Use the Task 2 monkeypatch, or temporarily edit the data, to check the empty state. Revert both afterwards.

## Task 4 — Final check against the spec

- `pytest -q`: all tests pass, including the original 7, which should be unchanged.
- Go through acceptance criteria 1–11 in the spec and tick each one.
- `git diff`: confirm the change is limited to `risk.py`, `api.py`, the frontend files, the tests and these docs. There should be no data, model or dependency changes.

## Risks and assumptions to watch in review

- **Duplicated rule:** an agent may write `delay >= 10` in the endpoint or in JS. Reject this and use `is_at_risk`.
- **Changing `/api/orders`:** filtering or adding fields there breaks existing consumers and tests.
- **Unknown delay as 0 or ∞:** sorting with `delay or 0`, or treating `None` as urgent, breaks the rule and the product constraint.
- **Route shadowing:** `/api/orders/at-risk` works in Flask but reads like an order id. The spec uses `/api/at-risk-orders`.
- **Monkeypatch target:** see Task 2.
- **XSS:** new cards use escaped values. The existing `orderCard` also uses raw `innerHTML`, which is left unchanged (out of scope, but worth noting).
- **Midnight rollover:** the `promised_eta` string sort assumes a single day (spec D6).

## Files touched

| File | Change |
|---|---|
| `backend/services/risk.py` | + `at_risk_queue()` |
| `backend/api.py` | + `/api/at-risk-orders` route |
| `tests/test_at_risk_orders.py` | **new**: queue unit tests and endpoint tests (existing test files unchanged) |
| `frontend/index.html` | + queue section and detail panel |
| `frontend/app.js` | + queue loading, detail view, `escapeHtml` |
| `frontend/styles.css` | + queue and detail styles |
