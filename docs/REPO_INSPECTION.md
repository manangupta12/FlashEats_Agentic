# Repository Inspection — At-Risk Orders Queue

Read-only inspection done before implementing the At-Risk Orders Queue ([features/at-risk-orders-starter.md](features/at-risk-orders-starter.md)). No code was changed.

The tests were not run during this inspection because pytest was not installed in the local environment. Run `pip install -r requirements.txt` before `pytest -q`.

## 1. Current architecture

```text
Browser → Flask API → service layer → JSON file
```

See [architecture.md](architecture.md).

| File | Role |
|---|---|
| `app.py` | Calls `create_app()` and serves on 127.0.0.1:5000 |
| `backend/api.py` | All HTTP routes; also serves `frontend/` as static files |
| `backend/services/orders.py` | Fetches orders |
| `backend/services/risk.py` | Holds the risk rule |
| `backend/models.py` | `Order` TypedDict (not used anywhere) |
| `frontend/` | Plain HTML/JS/CSS, no framework |

The architecture docs rule out adding a database, a frontend framework, a queue or a new service, and ask for the smallest change that fits.

## 2. Existing APIs

| Route | Behaviour |
|---|---|
| `GET /api/orders` | Returns every order as-is, unfiltered, in file order |
| `GET /api/orders/<id>` | Returns one order, or `404 {"error": "order_not_found"}` |
| `GET /` | Serves `index.html` |

No endpoint returns risk information.

## 3. Source of order data

`backend/data/orders.json` holds 8 static orders. `load_orders()` re-reads the file on every call, with no caching. `get_order()` searches the list one by one.

| Order | Status | Delay (min) | At risk? | Notes |
|---|---|---|---|---|
| FE-48291 | ACTIVE | 18 | Yes | Support opened; ETA_MESSAGE already sent |
| FE-48292 | ACTIVE | 6 | No | Below threshold |
| FE-48293 | ACTIVE | 14 | Yes | |
| FE-48294 | DELIVERED | 19 | No | Order is finished |
| FE-48295 | ACTIVE | null | No | Delay unknown; driver status SEARCHING |
| FE-48296 | CANCELLED | 21 | No | Order is cancelled |
| FE-48297 | ACTIVE | 10 | Yes | Exactly on the threshold |
| FE-48298 | ACTIVE | -3 | No | Running early |

With this data, the expected queue is **FE-48291, FE-48293, FE-48297**.

## 4. Business risk logic

`is_at_risk(order)` in `backend/services/risk.py` returns true only when all three conditions hold:

- `status == "ACTIVE"`
- the delay is known (`estimated_delay_minutes` is not null)
- the delay is at least 10 minutes

Its docstring says to keep this rule in one place and have callers reuse it. Right now nothing in the app calls it; only the tests do.

## 5. Relevant tests

- **`tests/test_risk.py`** covers four cases: exactly 10 minutes counts as at risk, 9 does not, a delivered order does not, and an unknown delay does not.
- **`tests/test_orders_api.py`** checks three things:
  - `/api/orders` returns exactly 8 orders, with FE-48291 first.
  - An unknown order ID returns a 404.
  - The order detail must **not** contain a `risk_score` field. This protects the existing API contract.
- **`tests/conftest.py`** provides a Flask test client fixture.

**Not covered:** cancelled orders, negative delays, and any queue or sorting behaviour.

## 6. Ambiguities and assumptions

1. **"Most urgent first" has no definition.** The obvious reading is highest `estimated_delay_minutes` first. Other possible signals are `support_opened`, `previous_intervention`, or driver status SEARCHING. Nothing says whether or how they count.
2. **Tie-breaking isn't specified.** Candidates are the promised ETA or the order ID.
3. **Unknown delay (FE-48295)** is excluded under the current rule, and the product docs say not to turn it into a number. Operations might still want to see it separately (for example, as "needs review"), but nothing says so.
4. **Negative delays** are valid data (early orders). The existing rule already handles them.
5. **Queue shape:** the queue could be a new endpoint (e.g. `GET /api/orders/at-risk`) or filtering in the browser. The architecture says business logic belongs in the backend, and the risk rule lives in Python, so a new endpoint is the better fit. Changing `/api/orders` would break its contract and its tests.
6. **What each row shows** ("enough to decide") isn't defined. Assumption: order ID, delay, promised and current ETA, restaurant and driver status, support opened, and previous intervention. These fields already exist, so nothing needs inventing.
7. **"Reuse the order-detail capability":** today, clicking an order only pops up an `alert()` with the URL. It's unclear whether a real detail view is in scope.
8. **Risk flag or score:** the tests forbid `risk_score` on the detail endpoint. It's unclear whether a new endpoint may add a computed field; the safest choice is to return plain orders.
9. **ETAs are bare "HH:MM" text** with no date or time zone. They are fine for display but unreliable for sorting.
10. **Status values** seen in the data are ACTIVE, DELIVERED and CANCELLED. The full list isn't documented.

## 7. Likely files to modify

| File | Change |
|---|---|
| `backend/services/risk.py` or `backend/services/orders.py` | Add a small `get_at_risk_orders()` that filters with `is_at_risk` and sorts by delay, highest first |
| `backend/api.py` | Add one route. Flask matches the literal `/api/orders/at-risk` ahead of `/api/orders/<order_id>`, so the two won't clash |
| `frontend/app.js`, `frontend/index.html` | Add the queue section, an empty state, and click-through to `/api/orders/<id>` |
| `frontend/styles.css` | Minor styling, if any |
| `tests/test_risk.py`, `tests/test_orders_api.py` | Cover the filter, the order (FE-48291, FE-48293, FE-48297), the empty queue, and a check that `/api/orders` still returns 8 |

No new files, dependencies or data fields should be needed.

## Key open question

What does "most urgent" mean (ambiguity #1)? Sorting by delay, highest first, is the smallest reasonable default. Confirm it with Operations before the spec is final.