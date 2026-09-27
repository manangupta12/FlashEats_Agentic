# Technical Spec — At-Risk Orders Queue

Companion to `docs/features/at-risk-orders-spec.md` (product spec) and
`docs/features/at-risk-orders-plan.md` (task breakdown).
The findings below come from reading the repository. Nothing here is taken from the README alone.

## 1. Current architecture

```text
Browser (frontend/, static, vanilla JS)
  ↓  fetch()
Flask API            backend/api.py        — owns HTTP routes
  ↓
Service layer        backend/services/     — orders.py (retrieval), risk.py (business rule)
  ↓
JSON source data     backend/data/orders.json
```

- Entry point: `app.py` calls `backend.api.create_app()`. The Flask dev server runs on `127.0.0.1:5000` with `debug=True`.
- Flask serves `frontend/` as the static root (`static_url_path=""`). `/` returns `index.html`.
- Dependencies: Flask 3.0.3 and pytest 8.3.3. Nothing else.
- `docs/architecture.md` asks for the smallest change that fits this shape: no database, no frontend framework, no queue, no new service.
- The frontend must consume backend APIs. It must not read `orders.json` directly.

## 2. Existing APIs

| Route | Handler | Behavior |
|---|---|---|
| `GET /api/orders` | `list_orders` | `jsonify(load_orders())`: the full list of raw order dicts, in file order |
| `GET /api/orders/<order_id>` | `order_detail` | The order dict, or `404 {"error": "order_not_found"}` |
| `GET /` | `index` | Serves `frontend/index.html` |

`api.py` imports `get_order` and `load_orders` **by name** (`from backend.services.orders import ...`).
This matters for monkeypatching in tests (see §9).

## 3. Data source

The data lives in `backend/data/orders.json`. `load_orders()` reads it fresh on every call, with no cache.
`get_order()` is a linear scan over `load_orders()`.

Order shape, from `backend/models.py::Order` (a TypedDict that is declared but not used anywhere at runtime):

| Field | Type |
|---|---|
| `order_id` | `str` |
| `status` | `str`. Observed values: `ACTIVE`, `DELIVERED`, `CANCELLED` |
| `promised_eta` | `str`: zero-padded `"HH:MM"`, with no date |
| `current_eta` | `str \| None` |
| `estimated_delay_minutes` | `int \| None`. Can be negative (running early) |
| `restaurant_status` | `str` |
| `driver_status` | `str`. Mixes enum-like values (`ASSIGNED`, `SEARCHING`) with free text (`"1.8 km away"`) |
| `support_opened` | `bool` |
| `previous_intervention` | `str \| None` |

The 8 sample orders and how the existing rule classifies them:

| order_id | status | delay | at risk | why |
|---|---|---|---|---|
| FE-48291 | ACTIVE | 18 | ✅ | active, ≥ 10 |
| FE-48292 | ACTIVE | 6 | ❌ | below threshold |
| FE-48293 | ACTIVE | 14 | ✅ | active, ≥ 10 |
| FE-48294 | DELIVERED | 19 | ❌ | not ACTIVE |
| FE-48295 | ACTIVE | `null` | ❌ | unknown delay |
| FE-48296 | CANCELLED | 21 | ❌ | not ACTIVE |
| FE-48297 | ACTIVE | 10 | ✅ | boundary: `>=` includes it |
| FE-48298 | ACTIVE | -3 | ❌ | running early |

Expected queue: `FE-48291 (18)`, `FE-48293 (14)`, `FE-48297 (10)`.

## 4. Business logic

`backend/services/risk.py::is_at_risk(order) -> bool` is the single source of truth.
Its docstring says: *"Keep this rule centralized. Callers should reuse it rather than
duplicating it."*

An order is at risk only if all three conditions hold:

- `status == "ACTIVE"`
- `estimated_delay_minutes is not None`
- `estimated_delay_minutes >= 10`

The `is not None` guard is deliberate. `docs/product_context.md` requires that
"Unknown delay should not be silently converted into a numeric risk value".
Patterns such as `delay or 0`, `.get(..., 0)` or treating `None` as ±∞ in a sort key
would all turn "unknown" into a number and break that rule.

Ordering is **not** part of `is_at_risk`. The new code adds it (§7).

## 5. Relevant tests

- `tests/conftest.py`: a single `client` fixture (`create_app()` with `TESTING=True`).
- `tests/test_risk.py`: unit tests for the rule, built on a local `make_order(**overrides)`
  factory, which is controlled data rather than the live JSON. It covers:
  - the threshold is inclusive at 10
  - 9 is below the threshold
  - a `DELIVERED` order with a 25-minute delay is not at risk
  - a `None` delay is not at risk

  New unit tests should follow this pattern.
- `tests/test_orders_api.py`: contract tests that must keep passing:
  - `/api/orders` returns exactly 8 orders, and the first is `FE-48291`
  - an unknown id returns 404 `{"error": "order_not_found"}`
  - the order payload has no `risk_score` and does have `estimated_delay_minutes`

These tests constrain the change. The existing list endpoint must not be filtered or reordered,
and no risk field may be added to the order payload.

Environment note: Flask is not currently installed locally, so `conftest.py` fails at import.
Run `pip install -r requirements.txt` before running the baseline.

## 6. Current frontend

- `index.html` has one "Active Orders" header, a `#message` line and an `#orders` container.
- `app.js` has two functions:
  - `loadOrders()` fetches `/api/orders` and renders `orderCard()` buttons into the container.
  - `orderCard()` shows the id, status, promised ETA and delay (it already renders `null` as "Unknown delay").
- Clicking a card only calls `window.alert(...)` with the detail URL. **There is no detail view in the UI.**
- Cards are built with template strings and `innerHTML` without escaping.
- `orderCard()` doesn't show the extra fields the spec needs (current ETA, restaurant or driver status,
  support, previous intervention), so the queue needs its own card renderer.

## 7. Design

### Service: `backend/services/risk.py`

```python
def at_risk_queue(orders: list[dict]) -> list[dict]:
    return sorted(
        (o for o in orders if is_at_risk(o)),
        key=lambda o: (-o["estimated_delay_minutes"], o["promised_eta"], o["order_id"]),
    )
```

- Filtering happens before sorting, so the delay in the sort key is always an `int`.
- It is a pure function that takes `orders` as input. It has no I/O and is easy to test with controlled fixtures.
- It returns the original dicts, with no added keys.
- The tie-breaks (`promised_eta` ascending, then `order_id`) make the order deterministic (spec D1).
  The string sort on `promised_eta` is correct only within a single day (spec D6).

### API: `backend/api.py`

```python
@app.get("/api/at-risk-orders")
def at_risk_orders():
    return jsonify(at_risk_queue(load_orders()))
```

- The route layer stays thin, following the existing pattern.
- It returns a plain JSON array, with the same element shape as `/api/orders` and no envelope.
- An empty result is `200 []`, not `404`.

### Frontend

- A new "At-risk orders" section above the existing list. It has its own message element and container.
- `loadAtRiskOrders()` renders the cards in the order the server returns them. It does **not** re-filter or re-sort.
- Loading, empty and error states follow the spec. A failure in the queue does not block `loadOrders()`.
- Clicking a card fetches `/api/orders/${encodeURIComponent(id)}` and renders the result in an `#order-detail` panel.
  The panel handles 404 and network errors.
- The new markup uses an `escapeHtml()` helper. The existing `orderCard()` / `loadOrders()` are left unchanged.

## 8. Assumptions

- Adding a route in `create_app()` is the expected extension point. No blueprint,
  router module or service class is needed at this size.
- The queue logic belongs in `risk.py`, which owns the risk rule. `orders.py` stays focused on retrieval,
  and `api.py` combines the two.
- Reading the file on every request (no caching) is acceptable at this data size.
- A single service day is assumed for ETA ordering.

## 9. Files to modify

| File | Change |
|---|---|
| `backend/services/risk.py` | add `at_risk_queue(orders)`. `is_at_risk` is unchanged |
| `backend/api.py` | add `GET /api/at-risk-orders` and the import |
| `tests/test_at_risk_orders.py` | **new**: queue unit tests over `make_order` fixtures (filter, boundary, exclusions, ordering, tie-breaks, empty, no mutation) and endpoint tests (seed ids and order, same keys as `/api/orders`, empty → `200 []`, existing endpoints unaffected) |
| `frontend/index.html` | add the queue section, state message and detail panel |
| `frontend/app.js` | fetch the queue, render states, detail view, `escapeHtml` |
| `frontend/styles.css` | minimal styles for the queue, delay badge and detail panel |

Not modified: `backend/services/orders.py`, `backend/models.py` (no new fields),
`backend/data/orders.json`, `requirements.txt`, and the existing test cases.

## 10. Risks

- **Duplicating the rule** (`>= 10` in the route or in JS): forbidden. Use `is_at_risk`.
- **A `None` delay in the sort key** would raise `TypeError`, or be coerced to a number. Filter first.
- **Changing `/api/orders`** (filtering, reordering, adding fields) breaks existing contract tests and consumers.
- **Testing against the live `orders.json` only** makes tests brittle and describes the data rather than the behavior.
  Unit tests use controlled fixtures. One API test checks the expected ids against the seed data as an acceptance check.
- **Monkeypatch target**: patch `backend.api.load_orders`, not `backend.services.orders.load_orders`.
  `api.py` imports the name directly, so patching the source module doesn't affect the route.
- **XSS**: the new UI escapes all interpolated values. The existing `orderCard()` does not (a known issue, out of scope).
- **Midnight rollover**: `"HH:MM"` string ordering is wrong across days. This is out of scope.

## 11. Alternatives considered

| Option | Why not chosen |
|---|---|
| `GET /api/orders/at-risk` | Werkzeug does rank the static rule above `<order_id>`, so it would route correctly. But the path reads like an order id and couples the queue to the detail route's namespace. `/api/at-risk-orders` is unambiguous. |
| `?at_risk=true` on `/api/orders` | It overloads a stable contract and adds filtering and sorting to an endpoint whose tests expect file order. |
| Queue function in `orders.py` | It would mix the risk rule's ordering with retrieval. A pure function in `risk.py` stays independent of I/O and next to the rule it depends on. |
| Filtering on the client | It would duplicate the rule in JS and violate the `risk.py` docstring. |
| Adding to `test_risk.py` / `test_orders_api.py` | Keeping the feature's tests in one new file leaves the existing contract tests untouched and makes the feature easy to review. |
