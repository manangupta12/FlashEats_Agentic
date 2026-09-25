# At-Risk Orders MVP Build Plan

## Objective

Build a small Operations queue that displays active orders meeting the
existing risk rule, puts the highest delays first, and lets an Operations
Manager inspect an order through the existing detail capability.

## MVP Decisions

These decisions make the current specs implementable while preserving existing
API contracts:

- Add a dedicated `GET /api/orders/at-risk` endpoint.
- Return complete existing order objects rather than inventing a summary
  schema or adding a `risk_score`.
- Use descending `estimated_delay_minutes` as the urgency order.
- Preserve JSON order for equal delays through a stable sort.
- Load the queue on page load.
- Selecting an item fetches `GET /api/orders/<order_id>` and renders the detail
  response in the existing page.
- Return `200` with `[]` when there are no at-risk orders.
- Use explicit loading, empty, and request-error states in the UI.
- Defer automatic refresh until a later iteration.

## Implementation Status

The MVP implementation is complete. The phases below record what was built and
how it was verified.

## Implementation Phases

### 1. Add the queue service

File: `backend/services/orders.py`

- Import the existing `is_at_risk` helper.
- Add a function that loads orders with `load_orders()`.
- Filter by calling `is_at_risk(order)` for every order.
- Sort the filtered list by `estimated_delay_minutes` descending.
- Keep the existing order for ties.
- Do not alter `load_orders()` or `get_order()` behavior.

Completed: the service reuses the centralized predicate and sorting behavior is
covered through isolated API tests.

### 2. Expose the queue API

File: `backend/api.py`

- Import the new service function.
- Register `GET /api/orders/at-risk`.
- Return the service result with `jsonify()`.
- Keep `/api/orders` and `/api/orders/<order_id>` unchanged.

Completed: endpoint tests verify filtering, ordering, payload preservation, and
the empty response.

### 3. Extend backend tests

Files: `tests/test_orders_api.py`, `tests/test_risk.py`

Add tests covering:

- Only `ACTIVE` orders with known delay of at least 10 minutes are returned.
- The 10-minute boundary is included.
- Delays are sorted highest first.
- Delivered and cancelled orders are excluded.
- Unknown delays are excluded.
- Empty results return HTTP `200` and `[]`.
- Existing list, detail, 404, and no-`risk_score` contracts still pass.

All API tests use a temporary test-owned dataset through `tests/conftest.py`.
They do not read `backend/data/orders.json`, assert production IDs, or rely on
production record counts. Test data is created only for the behavior under
test.

### 4. Build the queue UI

Files: `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`

- Add a dedicated queue container if the existing markup does not provide one.
- Fetch `/api/orders/at-risk` when the page loads.
- Render each order with at least its ID and delay, plus useful existing order
  fields such as ETA and operational statuses.
- Make each item selectable.
- Fetch `/api/orders/<order_id>` when selected and render the full details.
- Show a loading state while the queue request is pending.
- Show a clear empty state when the response is `[]`.
- Show a recoverable error state when the queue or detail request fails.
- Keep the UI framework-free and consistent with the existing frontend.

### 5. Run the full verification pass

Run:

```bash
pytest -q
```

The automated verification completed with:

```text
18 passed
```

Manual browser verification remains a follow-up task. When performed, verify
with controlled test data rather than relying on production fixture records:

- The queue shows only matching active orders.
- They appear in descending delay order.
- Delivered and cancelled orders do not appear.
- Selecting an item displays its existing detail response.
- The empty state can be observed with a controlled no-match fixture.

## Completion Criteria

The MVP is complete when:

- The new endpoint and UI use the centralized risk rule.
- Existing API behavior remains unchanged.
- Queue results are correctly filtered and ordered.
- The detail workflow works from a queue item.
- Empty, loading, and error states are usable.
- Automated tests pass and cover the acceptance criteria.
- No database, risk score, predictive model, or out-of-scope operations
  workflow has been introduced.

## Follow-Up Decisions

After the MVP, product can decide whether to add:

- Automatic polling or manual refresh.
- A secondary tie-breaker for equal delays.
- A narrower queue response schema.
- Additional queue fields or a dedicated detail view.