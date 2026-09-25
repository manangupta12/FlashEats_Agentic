# FlashEats Operations Repository Analysis

## 1. Business Context

### Facts from the repo
- This is an internal Operations dashboard for FlashEats, not a customer-facing product.
- The current objective is to help an Operations Manager focus on active orders that may require intervention now.
- The existing repo already defines the core risk rule: an order is at risk when it is ACTIVE and `estimated_delay_minutes >= 10`.
- Unknown delay values are not classified as risk.
- Completed and cancelled orders are not actionable risk items.
- The feature request for the at-risk queue is in `docs/features/at-risk-orders-starter.md`.
- The application currently inspects order data and exposes order detail endpoints.

### Inferences / assumptions
- This is a prototype or lightweight operational tool, not a full production logistics platform.
- The system is intended to help Ops triage active exceptions during busy service periods.
- Support activity is relevant to prioritization, especially since customer support is managed by Ops in this scope.

### Business entities
- Order: the main entity in `backend/data/orders.json`
- Fields include `order_id`, `status`, `promised_eta`, `current_eta`, `estimated_delay_minutes`, `restaurant_status`, `driver_status`, `support_opened`, and `previous_intervention`

## 2. System Overview

The simplest mental model is:

Browser UI -> Flask API -> Service Layer -> JSON Data Source

The app is intentionally small:
- `frontend/index.html` serves the page shell
- `frontend/app.js` fetches orders and renders order cards
- `backend/api.py` exposes the HTTP API
- `backend/services/orders.py` reads order data
- `backend/services/risk.py` contains the central risk business rule
- `backend/data/orders.json` is the data source

There are no external APIs, databases, auth systems, or queueing services in the current repo.

## 3. Repository Structure

### Backend API
- `backend/api.py` owns route definitions.
- It serves the UI at `/` and exposes `/api/orders` and `/api/orders/<order_id>`.

### Order access layer
- `backend/services/orders.py` reads the JSON file and returns either all orders or a single order.
- This is the data-access layer for the current scope.

### Risk logic
- `backend/services/risk.py` contains the rule used by Ops: active order + known delay + delay >= 10 minutes => at risk.
- This is the authoritative business rule in the repo.

### Data source
- `backend/data/orders.json` is the operational dataset for the app.
- It contains order records and their operational metadata.

### Frontend
- `frontend/index.html` is the page shell.
- `frontend/app.js` loads the data from the backend and renders cards for each order.

## 4. Core Workflows

### Workflow 1: list all orders
- Business event: Ops loads the dashboard
- Entry point: `GET /api/orders` in `backend/api.py`
- Important code: `list_orders()` and `load_orders()`
- Result: the UI receives the current order list and renders cards

### Workflow 2: inspect a specific order
- Business event: Ops looks up an individual order
- Entry point: `GET /api/orders/<order_id>`
- Important code: `order_detail()` and `get_order()`
- Result: a single order payload is returned, or a 404 if missing

### Workflow 3: classify an order as at risk
- Business event: Ops needs to know whether intervention is required
- Important code: `is_at_risk(order)` in `backend/services/risk.py`
- Rule: status must be ACTIVE, delay must be known, delay must be at least 10 minutes
- Result: risk classification used to guide intervention prioritization

### Workflow 4: render the dashboard
- Business event: browser loads the operations view
- Important code: `loadOrders()` and `orderCard(order)` in `frontend/app.js`
- Result: orders are displayed with delay information and basic order metadata

## 5. Code Deep Dive

### Entry points
- `app.py` starts the Flask app
- `backend/api.py` defines service routes and serves the frontend

### Core functions
- `create_app()` in `backend/api.py`
- `list_orders()`
- `order_detail(order_id)`
- `load_orders()`
- `get_order(order_id)`
- `is_at_risk(order)`

### Data contract
The repo uses a `TypedDict` named `Order` in `backend/models.py`. It describes the order fields used by the app.

### API behavior
- `GET /` serves the dashboard
- `GET /api/orders` returns all orders
- `GET /api/orders/<order_id>` returns one order or a 404

### Database and integrations
- No real database exists in this repo.
- No external systems are integrated.
- Data is served from the JSON source file.

### Error handling
- Missing order IDs result in a 404 `order_not_found` response.
- Frontend fetch errors are handled client-side with a user-visible message.

## 6. Data Model

The core entity is an order record in `backend/data/orders.json`.

Important fields:
- `order_id`
- `status`
- `promised_eta`
- `current_eta`
- `estimated_delay_minutes`
- `restaurant_status`
- `driver_status`
- `support_opened`
- `previous_intervention`

Key data states:
- `ACTIVE` means the order is currently actionable
- `DELIVERED` and `CANCELLED` indicate inactive cases that should not appear in the active intervention queue
- `estimated_delay_minutes` can be `null` or a numeric value; negative values are treated as data-quality issues

## 7. FDE-Relevant Understanding

### Real-world failure points
- Delay data may be missing or stale.
- Negative delay values indicate data-quality problems.
- Incomplete order metadata can affect triage accuracy.
- Static JSON is not a real operational data source, so production reliability depends on a later backend integration.

### Important operational concerns
- Ops must be able to tell why an order is in the queue
- Customer support tickets influence prioritization
- Risk classification should not be driven by cancelled or completed orders

### Risky areas to modify
- `backend/services/risk.py` because it defines business logic
- `backend/data/orders.json` because it is the current source of truth
- API contract behavior in `backend/api.py`

## 8. Practical Navigation Guide

- Need to change order retrieval behavior -> `backend/services/orders.py`
- Need to change risk definition -> `backend/services/risk.py`
- Need to change API behavior -> `backend/api.py`
- Need to change UI display -> `frontend/app.js`
- Need to understand the feature request -> `docs/features/at-risk-orders-starter.md`

## 9. Final Mental Model

FlashEats is building a small internal dashboard to help Operations identify active orders that require intervention. The repo is a prototype of that workflow, with a centralized risk rule that considers active status and delay threshold. The application is intentionally lightweight: browser UI, Flask API, service layer, and static JSON data. The key thing to remember is that the business logic is simple but operationally important, and the product should focus on triage rather than full lifecycle management or customer-facing functionality.
