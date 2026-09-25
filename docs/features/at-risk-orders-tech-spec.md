# Technical Spec — At-Risk Orders Queue

Companion to `docs/features/at-risk-orders-spec.md`.
Findings below come from reading the repository; nothing here is assumed from the README alone.

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

- Entry point: `app.py` → `backend.api.create_app()`, Flask dev server on `127.0.0.1:5000`.
- Flask serves `frontend/` as static root (`static_url_path=""`), `/` → `index.html`.
- Dependencies: Flask 3.0.3, pytest 8.3.3. Nothing else.
- `docs/architecture.md` explicitly asks for the smallest change that fits this shape:
  no database, no frontend framework, no queue, no new service.

## 2. Existing APIs

| Route | Handler | Behavior |
|---|---|---|
| `GET /api/orders` | `list_orders` | `jsonify(load_orders())` — full list, raw order dicts |
| `GET /api/orders/<order_id>` | `order_detail` | order dict, or `404 {"error": "order_not_found"}` |
| `GET /` | `index` | serves `frontend/index.html` |

Route naming convention: **all API routes live under `/api/orders`**, with
sub-resources nested beneath it. A new collection view belongs at `/api/orders/<something>`,
not at a sibling top-level path. The at-risk queue is therefore
`GET /api/orders/at-risk`.

Routing note: Werkzeug ranks a static rule above a rule with a converter, so
`/api/orders/at-risk` resolves to the queue handler and not to
`/api/orders/<order_id>`. This is asserted by a test rather than assumed.

## 3. Data source

`backend/data/orders.json`, read fresh on every call by `load_orders()` (no cache).

Order shape — `backend/models.py::Order` (TypedDict):

| Field | Type |
|---|---|
| `order_id` | `str` |
| `status` | `str` — observed: `ACTIVE`, `DELIVERED`, `CANCELLED` |
| `promised_eta` | `str` — `"HH:MM"` |
| `current_eta` | `str \| None` |
| `estimated_delay_minutes` | `int \| None` — can be negative (running early) |
| `restaurant_status` | `str` |
| `driver_status` | `str` |
| `support_opened` | `bool` |
| `previous_intervention` | `str \| None` |

Sample data (8 orders) and their classification under the existing rule:

| order_id | status | delay | at risk | why |
|---|---|---|---|---|
| FE-48291 | ACTIVE | 18 | ✅ | active, ≥ 10 |
| FE-48292 | ACTIVE | 6 | ❌ | below threshold |
| FE-48293 | ACTIVE | 14 | ✅ | active, ≥ 10 |
| FE-48294 | DELIVERED | 19 | ❌ | not ACTIVE |
| FE-48295 | ACTIVE | `null` | ❌ | unknown delay |
| FE-48296 | CANCELLED | 21 | ❌ | not ACTIVE |
| FE-48297 | ACTIVE | 10 | ✅ | boundary, `>=` includes it |
| FE-48298 | ACTIVE | -3 | ❌ | early |

Expected queue, sorted by delay desc: `FE-48291 (18)`, `FE-48293 (14)`, `FE-48297 (10)`.

## 4. Business logic

`backend/services/risk.py::is_at_risk(order) -> bool` is the single source of truth.
Its docstring states: *"Keep this rule centralized. Callers should reuse it rather than
duplicating it."*

Three independent conditions, all mandatory:
- `status == "ACTIVE"`,
- `estimated_delay_minutes is not None`,
- `estimated_delay_minutes >= 10`.

The `is not None` guard is deliberate: `docs/product_context.md` requires that
"Unknown delay should not be silently converted into a numeric risk value."
`.get()` with a default, `or 0`, or a truthiness check would all break this
(and `or 0` would additionally mis-handle a legitimate `0`).

Sorting is **not** part of `is_at_risk` and must be added by the caller.

## 5. Relevant tests

- `tests/conftest.py` — single `client` fixture, `create_app()` + `TESTING=True`.
- `tests/test_risk.py` — unit tests for the rule, built on a local `make_order(**overrides)`
  factory (a controlled fixture, **not** live JSON). Covers: threshold-inclusive at 10,
  below at 9, `DELIVERED` at 25, `None` delay. This is the pattern new tests should follow.
- `tests/test_orders_api.py` — contract tests that must keep passing:
  - `/api/orders` returns exactly 8 orders, first is `FE-48291`,
  - unknown id → 404 `{"error": "order_not_found"}`,
  - order payload has no `risk_score` and does have `estimated_delay_minutes`.

These constrain the change: the existing list endpoint must not be filtered or reordered,
and no risk field may be added to the order payload.

## 6. Assumptions

- Adding a route to `backend/api.py` is the expected extension point; no blueprint,
  router module, or service class is warranted at this size.
- Filtering + sorting belong in the **service layer** (`backend/services/orders.py`),
  keeping `api.py` a thin HTTP shell, matching the existing split.
- The at-risk endpoint returns the same raw order dicts as `/api/orders`, just filtered
  and ordered. No wrapper envelope, no computed fields — that keeps the frontend's
  existing `orderCard()` rendering reusable and satisfies "do not invent fields".
- Empty result is `200 []`, not `404`.
- Read-per-request (no caching) is acceptable at this data size.

## 7. Files to modify

| File | Change |
|---|---|
| `backend/services/orders.py` | add `get_at_risk_orders()` — filter via `is_at_risk`, sort by delay desc |
| `backend/api.py` | add `GET /api/orders/at-risk` returning `get_at_risk_orders()` |
| `tests/test_at_risk_orders.py` | **new** — behavioral tests over controlled fixtures (filter, boundary, exclusions, ordering) |
| `frontend/index.html` | add queue section + message/state container |
| `frontend/app.js` | fetch the at-risk endpoint; loading / empty / error states |
| `frontend/styles.css` | minimal styling for the queue and its states |

Not modified: `backend/services/risk.py` (rule unchanged), `backend/models.py`
(no new fields), `backend/data/orders.json`, existing tests.

## 8. Risks

- **Duplicating the rule** in the new code path — forbidden; import `is_at_risk`.
- **Sorting with a `None` delay** would raise `TypeError`; filtering happens first,
  so the sort key is always an `int`.
- **Testing against live `orders.json`** makes tests brittle — any data edit breaks
  unrelated assertions, and the tests then describe the data rather than the behavior.
  Use controlled fixtures, as `tests/test_risk.py` already does.
