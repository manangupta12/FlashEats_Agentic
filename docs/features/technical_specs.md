# Technical Specification: At-Risk Orders Queue

## 1. User
Operations Manager (System Implementation)

## 2. Goal
Implement the backend and frontend components to support the At-Risk Orders Queue efficiently using existing patterns.

## 3. Acceptance criteria
- The frontend must retrieve data using the backend API; no data filtering should happen blindly on the frontend if it can be avoided.
- The existing business logic in `backend/services/risk.py` (`is_at_risk` function) MUST be reused to determine if an order is at risk.
- A new API endpoint (e.g., `GET /api/orders/risk`) or a query parameter on the existing endpoint (e.g., `GET /api/orders?filter=risk`) will be implemented.
- The backend filtering logic must ensure that only orders with `status == "ACTIVE"` and `estimated_delay_minutes >= 10` are processed, explicitly ignoring unknown delays and non-active states.
- The sorting of orders by urgency (highest delay first) should be handled on the backend before returning the JSON payload.

## 4. Out of scope
- Changing the underlying data source from `orders.json` to a database in this MVP.
- Modifying the existing `Order` model schema.
- Re-writing the frontend to use a complex framework.

## 5. Open questions
- Is it preferred to add a query parameter (e.g. `?risk=true`) to the existing `/api/orders` endpoint, or to create a new dedicated endpoint like `/api/orders/risk`?
- Should we write additional unit tests for the sorting logic, or just test the API output?
