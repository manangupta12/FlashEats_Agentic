# Technical Spec: At-Risk Orders Queue

This technical spec outlines the implementation plan to fulfill the requirements of the Functional Spec, ensuring we adhere to the architectural boundaries and make minimal, safe changes.

## 1. Backend Service Layer (`backend/services/orders.py`)
- **Action**: Add a new function `get_at_risk_orders() -> list[dict]`.
- **Logic**: 
  - Call the existing `load_orders()` to retrieve all orders.
  - Filter the list using the `is_at_risk(order)` function imported from `backend.services.risk`.
  - Sort the filtered list in descending order based on the `estimated_delay_minutes` key to prioritize the most urgent orders.

## 2. Backend API Layer (`backend/api.py`)
- **Action**: Introduce a new HTTP GET endpoint to cleanly separate this feature from the general orders list.
- **Route**: `@app.get("/api/orders/at-risk")`
- **Logic**: Call `get_at_risk_orders()` and return the result using `jsonify()`. This preserves the existing `/api/orders` contract exactly as it is, fulfilling the "Existing API contracts should remain stable" constraint.

## 3. Frontend (`frontend/index.html` & `frontend/app.js`)
- **HTML Layout**: Add a new container section (e.g., `<div id="at-risk-orders-section">`) to `index.html` prominently placed to draw the Operations Manager's attention.
- **Data Fetching**: Create an `async function loadAtRiskOrders()` in `app.js` that performs a `fetch()` to `/api/orders/at-risk`.
- **Rendering**: 
  - If the returned array is empty, render a helpful empty state message inside the container (e.g., "✅ No at-risk orders currently require attention.").
  - If populated, map over the data reusing the existing `orderCard(order)` HTML string generation to maintain consistent UI.
- **Interactions**: Attach the same click event listeners to the new cards so that clicking them fires the existing `window.alert` pointing to the `/api/orders/<id>` route.

## 4. Testing (`tests/test_orders_api.py`)
- **Action**: Add a new test case `test_at_risk_orders_endpoint_returns_sorted_risky_orders(client)`.
- **Logic**: 
  - Make a GET request to `/api/orders/at-risk`.
  - Assert the HTTP status code is 200.
  - Assert that all returned items are truly "at risk" (e.g., verify their status and delay against the logic).
  - Assert that the items are correctly sorted by `estimated_delay_minutes` descending.

## Assumptions Addressed from Functional Spec
- **Secondary Sorting**: For simplicity in the MVP, we will only sort by `estimated_delay_minutes` descending. If two orders have the exact same delay, they will retain their original order in the JSON file (stable sort).
- **UI Placement**: The queue will be rendered in a separate, dedicated section on the main page rather than completely replacing the standard list, ensuring the manager still has a holistic view if needed.

## 5. Technical Acceptance Criteria
- **Architectural Boundaries Maintained**: HTTP route logic must stay exclusively in `backend/api.py`, and data retrieval logic must stay in `backend/services/orders.py`. No new databases or queues are introduced.
- **Logic Reusability**: The implementation must strictly import and use `is_at_risk(order)` from `backend/services/risk.py`. The rule logic must **not** be duplicated anywhere else.
- **Backward Compatibility (No Regressions)**: The existing `/api/orders` route and its payload must remain completely unchanged. All existing tests in `tests/test_orders_api.py` and `tests/test_risk.py` must continue to pass without modification.
- **Test Coverage**: A new automated test must be added to `test_orders_api.py` to verify that `GET /api/orders/at-risk` returns a 200 status code, applies the correct filter, and correctly sorts by `estimated_delay_minutes` in descending order.
- **DRY (Don't Repeat Yourself) Frontend**: The new frontend queue must reuse the existing `orderCard(order)` function in `app.js` to render the UI components. 
- **Safe DOM Manipulation**: The frontend must handle the scenario where the API returns an empty array `[]` cleanly without throwing JavaScript errors, rendering the specified empty state.
