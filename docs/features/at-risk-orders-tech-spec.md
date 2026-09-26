# Technical Spec — At-Risk Orders Queue

Functional spec: [`at-risk-orders-func-spec.md`](at-risk-orders-func-spec.md). Criteria are referenced as **AC-n**.
Status: Tasks 1–2 implemented (backend endpoint and tests). UI tasks pending

## 1. Assumptions

This design takes the proposed defaults for the functional spec's open questions. If an answer changes, only the sections listed need updating.

| Open question | Assumed answer | Affects |
|---|---|---|
| OQ-1 ordering | `estimated_delay_minutes` descending, then `order_id` ascending | §3.1, §6 |
| OQ-2 unknown delay | Left out of the MVP. No separate list | §3.1, §3.3 |
| OQ-3 endpoint | New `GET /api/at-risk-orders` | §3.2, §4 |
| OQ-4 fields | The fields listed in AC-13 | §3.3 |
| OQ-5 layout | New section above the existing "Active Orders" list | §3.3 |
| OQ-6 detail | Inline detail panel filled from `GET /api/orders/<id>` | §3.3 |
| OQ-7 runtime | Python 3.10+ required. Documenting it is a separate task (T6) | §7 |

## 2. Design overview

The work follows the existing layers ([`docs/architecture.md`](../architecture.md)). No new modules, dependencies, or data stores are added.

```text
frontend/app.js ──fetch──▶ GET /api/at-risk-orders ──▶ at_risk_queue(load_orders())
                                                          │
                                                          ├─ filter: is_at_risk(order)   (unchanged)
                                                          └─ sort:   (-delay, order_id)

click entry ──fetch──▶ GET /api/orders/<id> (unchanged) ──▶ detail panel
```

## 3. Components

### 3.1 Service: `backend/services/risk.py` (add one function)

```python
def at_risk_queue(orders: list[dict]) -> list[dict]:
    """Return the orders that need intervention now, most urgent first.

    Membership is decided only by is_at_risk(). The queue is sorted by
    estimated delay, largest first, with ties broken by order_id.
    """
```

- **Filtering:** `[o for o in orders if is_at_risk(o)]`. The risk conditions are not repeated here (AC-1).
- **Sorting:** `sorted(..., key=lambda o: (-o["estimated_delay_minutes"], o["order_id"]))`. Negating the delay is safe because `is_at_risk` only lets through orders whose delay is known and ≥ 10.
- **Return value:** the original order dicts, unchanged. No computed fields are added (AC-9).
- **Why a pure function that takes a list:**
  - `risk.py` already owns the rule, so the queue logic sits next to it.
  - Taking the orders as a parameter keeps `risk.py` from importing the data layer.
  - Tests can pass in their own lists, including an empty one, without patching file reads.
- `is_at_risk()` itself is **not modified** (AC-19).

### 3.2 API: `backend/api.py` (add one route)

```python
@app.get("/api/at-risk-orders")
def at_risk_orders():
    return jsonify(at_risk_queue(load_orders()))
```

- **No route overlap:** the path sits outside `/api/orders/...`, so it can't clash with `/api/orders/<order_id>`. No order ID is hidden, and the existing routes are untouched.
- **Always `200`:** the route returns `200`, including `[]` when nothing is at risk (AC-10).
- **Existing routes and handlers:** unchanged (AC-11).

### 3.3 Frontend: `frontend/index.html`, `app.js`, `styles.css`

**`index.html`.** Add the following above the existing `#message` and `#orders`, and leave those elements as they are:

```html
<section class="queue">
  <h2>Needs attention</h2>
  <div id="queue-message" class="message">Loading at-risk orders…</div>
  <div id="queue" class="orders"></div>
</section>
<section id="order-detail" class="detail" hidden></section>
```

**`app.js`.** Add:

- **`loadAtRiskQueue()`**
  - Fetches `/api/at-risk-orders` and renders one card per order (AC-12).
  - Shows an empty-state message for `[]`, e.g. "No active orders currently need intervention." (AC-15).
  - Shows "Could not load at-risk orders: …" on failure, matching the existing pattern (AC-16).
- **`queueCard(order)`**
  - Shows the AC-13 fields.
  - A `formatValue` helper turns `null` into "None" (or "Unknown" for ETAs) and `support_opened` into "Support open" / "No support ticket". Null is never shown as `0` or `null` (AC-13).
- **`showOrderDetail(orderId)`**
  - Fetches `/api/orders/<id>` and shows every field in `#order-detail` (AC-14).
  - Shows "Order not found" on a 404 and a generic error message for any other failure.

The browser never reads `orders.json` and never applies the risk rule (AC-12). The existing `loadOrders()`, `orderCard()` and their `window.alert` click handler are left unchanged.

**Escaping:** the existing code builds HTML with template strings and `innerHTML`. The new rendering code should add a small `escapeHtml()` helper for values taken from the data. The data is internal, but `driver_status` already holds free text (`"1.8 km away"`), so it shouldn't be trusted as markup.

**`styles.css`.** Add a few small rules for `.queue`, `.detail` and the section heading, reusing the existing `.order-card` look.

## 4. API contract

### `GET /api/at-risk-orders` (new)

| Case | Status | Body |
|---|---|---|
| Orders at risk | `200` | JSON array of order objects, in queue order |
| None at risk | `200` | `[]` |

Each item has exactly the stored order fields: `order_id`, `status`, `promised_eta`, `current_eta`, `estimated_delay_minutes`, `restaurant_status`, `driver_status`, `support_opened`, `previous_intervention`. There is no `risk_score` and no other added field. The endpoint ignores query parameters.

Response with the current data:

```json
[
  {"order_id": "FE-48291", "estimated_delay_minutes": 18, "...": "..."},
  {"order_id": "FE-48293", "estimated_delay_minutes": 14, "...": "..."},
  {"order_id": "FE-48297", "estimated_delay_minutes": 10, "...": "..."}
]
```

### Existing endpoints (unchanged)

- `GET /api/orders` returns all 8 orders, in file order.
- `GET /api/orders/<order_id>` returns `200` with the order, or `404 {"error": "order_not_found"}`.

## 5. Test plan

The tests go in a new file, `tests/test_at_risk_queue.py`. The existing test files are not edited (AC-18).

### Unit tests: `at_risk_queue()` with hand-built order lists

| Test | Proves |
|---|---|
| DELIVERED and CANCELLED orders with large delays are excluded | AC-2 |
| An ACTIVE order with `estimated_delay_minutes=None` is excluded | AC-3 |
| An order at 10 is included; orders at 9 and at −3 are excluded | AC-4 |
| Sorted by delay descending | AC-6 |
| Equal delays are ordered by `order_id` ascending | AC-6 |
| An empty input list returns `[]` | AC-10 |
| No at-risk orders in the input returns `[]` | AC-10 |
| Returned dicts have the same keys as the input (no added fields) | AC-9 |
| Membership matches `[o for o in orders if is_at_risk(o)]` | AC-1 |

### API tests: using the `client` fixture

| Test | Proves |
|---|---|
| `GET /api/at-risk-orders` returns `200` and the IDs `["FE-48291", "FE-48293", "FE-48297"]` | AC-5, AC-7, AC-8 |
| No item has a `risk_score` field | AC-9 |
| An empty queue returns `200 []`. Use `monkeypatch.setattr("backend.api.load_orders", lambda: [])` | AC-10 |
| `GET /api/orders` still returns all 8 orders in file order | AC-11 |
| `GET /api/orders/FE-48291` still returns that order, and an unknown ID still returns 404 | AC-11 |

**Monkeypatch gotcha:** `api.py` imports `load_orders` by name, so patch `backend.api.load_orders`. Patching `backend.services.orders.load_orders` has no effect on the route.

### Frontend

There's no JavaScript test harness, and adding one is out of scope. Instead, check these by hand in the browser:

- the queue shows 3 cards in the right order;
- null values are shown as labels;
- clicking a card fills the detail panel;
- the empty state appears, e.g. when temporarily patched to return `[]` locally (never committed);
- the error state appears when the server is stopped.

### Command

```bash
venv/bin/python -m pytest -q    # venv must be Python 3.10+
```

Expected result: 7 existing tests plus the new tests, all passing.

## 6. Task breakdown

Each task is a separate, reviewable diff and ends with a test run.

| # | Task | Files | Done when |
|---|---|---|---|
| T1 | Add `at_risk_queue()` and its unit tests | `risk.py`, `tests/test_at_risk_queue.py` | Unit tests pass; `is_at_risk` diff is empty |
| T2 | Add the `GET /api/at-risk-orders` route and its API tests | `api.py`, `tests/test_at_risk_queue.py` | All tests pass, including the unchanged-contract tests |
| T3 | Add the queue section to the UI, with empty and error states | `index.html`, `app.js`, `styles.css` | Manual check: 3 cards, correct order, empty and error states work |
| T4 | Add the order-detail panel for queue clicks | `index.html`, `app.js`, `styles.css` | Manual check: clicking shows the full order; 404 is handled |
| T5 | Check every AC against the functional spec | — | Every AC is ticked or explicitly deferred |
| T6 | *(optional, OQ-7)* Add a "Python 3.10+" note to the README | `README.md` | — |

## 7. Risks and trade-offs

| Risk | Mitigation |
|---|---|
| The venv uses Python 3.9 and fails on `X \| None` hints | Recreate the venv with 3.10+ (Homebrew 3.13 is available); T6 documents this |
| API tests read the real `orders.json`, so data edits break them | Don't edit the data; the empty case uses monkeypatch |
| Urgency ranking (OQ-1) may change | Sorting lives in one key function in `at_risk_queue()` |
| Unknown-delay orders (FE-48295) are invisible in the queue | This follows the rule and product context. Flagged to Operations as OQ-2 |
| No automated frontend tests | Keep the JS logic thin; the backend holds all rule and sort logic, and that is tested |
| `innerHTML` rendering of free-text data | Use `escapeHtml()` in the new rendering code |
