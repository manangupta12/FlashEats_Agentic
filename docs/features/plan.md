# Implementation Plan: At-Risk Orders Queue

This document outlines the step-by-step minimal implementation plan for the At-Risk Orders Queue feature.

## 1. Backend API Changes (`backend/api.py`)
- **Modify existing endpoint:** Update `GET /api/orders` to accept an optional query parameter, `?risk=true`.
- **Filtering:** If `risk=true` is present in the request, use the existing `is_at_risk(order)` function from `backend/services/risk.py` to filter the list of orders returned by `load_orders()`.
- **Sorting:** Sort the filtered at-risk orders descending by `estimated_delay_minutes` so the most urgent orders appear first. 

## 2. Frontend UI Changes (`frontend/index.html` & `frontend/app.js`)
- **Add a toggle control:** Introduce a simple checkbox or toggle in `index.html` (e.g., "Show At-Risk Orders Only") to allow Operations to switch between viewing all orders and just the at-risk queue.
- **Update data fetching:** Modify `loadOrders()` in `app.js` to read the toggle state and conditionally append `?risk=true` to the `fetch` URL.
- **Handle the empty state:** When the response is empty and the risk toggle is on, update the `messageEl.textContent` to show a clear empty state message (e.g., "No orders currently at risk. You're all caught up!").
- **Card tweaks:** Visually distinguish at-risk orders by making the delay text red to make the queue immediately actionable.
- **Re-use behavior:** Ensure clicking an order card still alerts with the existing `/api/orders/<id>` capability.

## 3. Backend Tests (`tests/test_orders_api.py`)
- **Add tests for the `?risk=true` query parameter:**
  - Verify that only orders matching the `is_at_risk` condition are returned.
  - Verify that the returned list is correctly sorted descending by `estimated_delay_minutes`.
  - Verify that when no orders are at risk, it correctly returns an empty JSON list `[]`.
