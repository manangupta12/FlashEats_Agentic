# At-Risk Orders Queue Technical Specification

## Current Architecture
Minimalist architecture:
- **Frontend**: Vanilla JS + HTML (`frontend/`). Fetches data from `/api/*`.
- **Backend API**: Flask (`backend/api.py`, `app.py`).
- **Service Layer**:
  - `backend/services/orders.py` (Order retrieval)
  - `backend/services/risk.py` (Risk logic)
- **Data Source**: Static JSON file (`backend/data/orders.json`). No database.

## Existing APIs
- `GET /api/orders`: Returns all orders.
- `GET /api/orders/<order_id>`: Returns detail for a specific order (or 404).
- `GET /`: Serves `frontend/index.html`.

## Source of Order Data
- `backend/data/orders.json` containing 8 seed orders with varying statuses (`ACTIVE`, `DELIVERED`, `CANCELLED`), delays, and intervention states.

## Business Risk Logic
Located in `backend/services/risk.py` -> `is_at_risk(order)`:
- Order status must be "ACTIVE".
- `estimated_delay_minutes` must be `not None`.
- `estimated_delay_minutes` must be `>= 10`.

## Architecture Decisions
- The frontend must fetch this data via a backend API rather than reading the JSON file directly.
- No new databases, frontend frameworks, or external queues will be introduced.

## Relevant Tests
- `tests/test_risk.py`: Covers risk threshold boundaries, status checks, and null delays.
- `tests/test_orders_api.py`: Asserts API payload structures and existing endpoints. Notably asserts `risk_score` is not exposed on existing endpoints.
- **Testing Strategy**: New endpoint tests must use controlled fixtures/mocks (e.g., patching `load_orders`) rather than relying on live `orders.json` data or hardcoded IDs, to ensure robustness.

## Assumptions / Ambiguities
- It is assumed that we should create a new backend endpoint (e.g., `/api/orders/at-risk`) to perform the filtering and sorting on the server side, keeping logic out of the frontend.
- It is assumed that sorting descending by `estimated_delay_minutes` satisfies the "most urgent orders first" requirement.
- **Data returned**: It is assumed the backend will return the full order object for the queue, but only the necessary fields will be rendered on the frontend.

## Likely Files to Modify
- `backend/api.py`: To add a new endpoint for at-risk orders.
- `frontend/app.js`: To fetch and render the new at-risk queue.
- `frontend/index.html`: To add a container for the at-risk queue.
- `frontend/styles.css`: To style the new queue and empty state.
- `tests/test_orders_api.py`: To add test coverage for the new endpoint.
