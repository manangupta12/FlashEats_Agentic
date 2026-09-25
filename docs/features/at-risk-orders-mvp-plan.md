# At-Risk Orders MVP Plan

## Objective

Ship an operations queue that surfaces active at-risk orders, orders them by
highest delay first, and allows quick inspection through existing order detail.

## Key Decisions

- Add a dedicated `GET /api/orders/at-risk` endpoint
- Return existing order objects without introducing `risk_score`
- Sort by `estimated_delay_minutes` descending
- Keep sort stability for equal delays
- Load queue on page initialization
- Reuse existing detail endpoint on queue item click
- Return `200` with an empty array for no matches
- Show loading, empty, and error states in UI

## Delivery Phases

### 1) Queue service support

File: `backend/services/orders.py`

- Import and reuse `is_at_risk`
- Filter loaded orders with the predicate
- Sort filtered list by delay descending
- Preserve existing `load_orders()` and `get_order()` behavior

### 2) Queue API route

File: `backend/api.py`

- Register `GET /api/orders/at-risk`
- Return filtered service output with `jsonify`
- Keep existing routes unchanged

### 3) Isolated API fixtures and tests

Files: `tests/conftest.py`, `tests/test_orders_api.py`

- Replace production-coupled assertions with fixture-owned data
- Add queue route tests for filtering, sorting, and empty results
- Confirm payload shape and no `risk_score` regression
- Keep existing 404 behavior checks

### 4) Risk predicate tests

File: `tests/test_risk.py`

- Add boundary and exclusion coverage using parametrized tests
- Validate status and unknown-delay exclusions

### 5) Frontend queue and detail panel

Files: `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`

- Add queue section plus all-orders section
- Fetch and render at-risk queue on load
- Keep card click behavior but show inline detail panel
- Add empty and error handling for both lists
- Keep solution framework-free

### 6) Verification

Command:

```bash
pytest -q
```

Expected validation outcomes:

- queue endpoint and frontend behavior match business intent
- existing list and detail contracts remain stable
- tests pass using isolated fixture data
