# Technical Specification: At-Risk Orders Dashboard (V1)

## 1. Overview & Architecture

### System Context
The At-Risk Orders Dashboard is an operational tool built on the existing lightweight architecture:
* **Backend:** Flask 3.0.3 (Python 3.11+)
* **Service Layer:** Python modules encapsulating business rules and data access
* **Data Source:** Flat JSON file (`backend/data/orders.json`)
* **Frontend:** Vanilla HTML5, CSS3, and JavaScript (ES6+)

```text
┌─────────────────────────────────────────────────────────┐
│              Browser Frontend (Vanilla JS)              │
│  - At-Risk Orders Table (5 columns, sorted by urgency)  │
│  - Detail Inspection Drawer/Panel (GET /api/orders/:id) │
│  - Empty State & Error States                           │
└──────────────┬────────────────────────────▲─────────────┘
               │ HTTP GET                   │ JSON
               ▼                            │
┌─────────────────────────────────────────────────────────┐
│                  Flask API (api.py)                     │
│  - GET /api/orders/at-risk (or GET /api/orders?filter)  │
│  - GET /api/orders/<order_id> (Detail)                  │
│  - GET /api/orders (Existing backward-compatible)       │
└──────────────┬──────────────────────────────────────────┘
               │ Calls
               ▼
┌─────────────────────────────────────────────────────────┐
│                     Service Layer                       │
│  - services/orders.py: load_orders(), get_order()       │
│                        get_at_risk_orders()             │
│  - services/risk.py:   is_at_risk()                     │
└──────────────┬──────────────────────────────────────────┘
               │ Reads
               ▼
┌─────────────────────────────────────────────────────────┐
│            JSON Data (backend/data/orders.json)         │
└─────────────────────────────────────────────────────────┘
```

### Architectural Constraints & Boundaries
1. **Minimal Architecture:** No external databases, frontend frameworks (React, Vue), message queues, or persistent background daemons.
2. **Layer Isolation:**
   * `backend/api.py` handles HTTP serialization, status codes, and routing.
   * `backend/services/orders.py` owns data retrieval, filtering, and ordering logic.
   * `backend/services/risk.py` owns the business rule defining risk classification.
   * `frontend/` consumes API endpoints and does not access server data files directly.
3. **Contract Stability:** Existing API responses for `GET /api/orders` and `GET /api/orders/<order_id>` must remain backward compatible. No synthetic fields (e.g. `risk_score`) are injected into the payload.

---

## 2. Backend Design & Implementation

### 2.1 Risk Service (`backend/services/risk.py`)
Reuses the centralized business rule without modification:
```python
def is_at_risk(order: dict) -> bool:
    """Classifies an order as actionable at-risk if:
    1. status == 'ACTIVE'
    2. estimated_delay_minutes is not None
    3. estimated_delay_minutes >= 10
    """
    delay = order.get("estimated_delay_minutes")
    return (
        order.get("status") == "ACTIVE"
        and delay is not None
        and delay >= 10
    )
```

### 2.2 Order Service (`backend/services/orders.py`)
Adds `get_at_risk_orders()` to retrieve and sort at-risk orders:
```python
def get_at_risk_orders() -> list[dict]:
    """Returns all active at-risk orders sorted by highest delay first."""
    all_orders = load_orders()
    at_risk = [order for order in all_orders if is_at_risk(order)]
    # Primary sort: estimated_delay_minutes descending
    # Secondary sort: promised_eta ascending (earliest promised delivery first)
    return sorted(
        at_risk,
        key=lambda o: (-o["estimated_delay_minutes"], o.get("promised_eta", ""))
    )
```

### 2.3 API Layer (`backend/api.py`)
Exposes the at-risk orders endpoint while preserving existing endpoints:
* **`GET /api/orders/at-risk`**: Returns JSON list of sorted at-risk orders.
* **`GET /api/orders`**: Returns all orders (unfiltered, preserving existing contract).
* **`GET /api/orders/<order_id>`**: Returns single order detail object or 404 `{"error": "order_not_found"}`.
* **`GET /`**: Serves `frontend/index.html`.

---

## 3. Data Schema

The data model conforms to [`Order`](file:///Users/tanu/code/FlashEats_Agentic/backend/models.py#L4-L14):

```python
class Order(TypedDict):
    order_id: str                      # Unique order ID (e.g., "FE-48291")
    status: str                        # "ACTIVE" | "DELIVERED" | "CANCELLED"
    promised_eta: str                  # HH:MM string (e.g., "19:42")
    current_eta: str | None            # HH:MM string or null
    estimated_delay_minutes: int | None # Integer minutes or null
    restaurant_status: str             # "PREPARING" | "READY" | "COMPLETED" | "CANCELLED"
    driver_status: str                 # Distance or state (e.g., "1.8 km away", "ASSIGNED")
    support_opened: bool               # True if support ticket active
    previous_intervention: str | None  # Code string (e.g., "ETA_MESSAGE") or null
```

---

## 4. Frontend Design & UI/UX Specifications

### 4.1 Layout & DOM Structure (`frontend/index.html`)
* **Header & Stat Badge:** Shows application title and live count of at-risk orders (e.g. `3 orders require attention`).
* **Table Container (`#at-risk-table`):** A 5-column table displaying at-risk items.
* **Empty State Banner (`#empty-state`):** Rendered with clear messaging when 0 at-risk orders are returned.
* **Order Detail Drawer/Modal (`#order-detail-drawer`):** Slide-over panel or expandable section displaying comprehensive order information when a row is clicked.

### 4.2 The 5 Essential Table Columns
| # | Column Name | Data Mapping | Display Example |
|---|---|---|---|
| 1 | **Order ID** | `order.order_id` | `FE-48291` |
| 2 | **Promised / Projected ETA** | `order.promised_eta` → `order.current_eta` | `19:42 → 20:00` |
| 3 | **Estimated Delay** | `order.estimated_delay_minutes` | `+18 min` (Red badge) |
| 4 | **Fulfillment Status** | `order.restaurant_status` + `order.driver_status` | `Restaurant: READY`<br>`Driver: 1.8 km away` |
| 5 | **Intervention / Action** | `order.support_opened` + `order.previous_intervention` | `Support: Open`<br>`[Inspect Order]` |

### 4.3 Detail Inspection Drawer Fields
When an order row is clicked, fetch `GET /api/orders/<order_id>` and display:
* **Order Header:** Order ID, Status (`ACTIVE`), Delay Pill.
* **Timing Breakdown:** Promised ETA, Current ETA, Delay in minutes.
* **Fulfillment Progress:** Restaurant Status, Driver Status.
* **Support & Interventions:** Support Ticket Open (`Yes`/`No`), Previous Intervention type (`ETA_MESSAGE`, `RESTAURANT_CONTACT`, `REFUND_OFFER`, or `None`).

### 4.4 Client-Side Script (`frontend/app.js`)
* `fetchAtRiskOrders()`: Invokes `GET /api/orders/at-risk`, handles loading state, empty state, error state, and renders table rows.
* `inspectOrder(orderId)`: Invokes `GET /api/orders/${orderId}`, renders detail panel content, and opens the drawer.
* `closeDetailDrawer()`: Dismisses inspection panel.

### 4.5 Styling (`frontend/styles.css`)
* Clean modern typography, accessible contrast, and visual hierarchy.
* Status pills: Red/Amber badges for delay (`>= 10 min`), Neutral for standard info.
* Interactive row hover effects and smooth slide transition for the detail drawer.

---

## 5. Testing & Quality Assurance Plan

### 5.1 Unit Tests (`tests/test_risk.py`)
Verify edge cases in risk evaluation logic:
* `estimated_delay_minutes == 10` → `True` (`test_active_order_at_threshold_is_at_risk`)
* `estimated_delay_minutes == 9` → `False` (`test_active_order_below_threshold_is_not_at_risk`)
* `status == "DELIVERED"` with `estimated_delay_minutes == 25` → `False` (`test_completed_late_order_is_not_actionable_risk`)
* `status == "CANCELLED"` with `estimated_delay_minutes == 21` → `False` (`test_cancelled_order_is_not_actionable_risk`)
* `estimated_delay_minutes is None` → `False` (`test_unknown_delay_is_not_classified_as_risk`)


### 5.2 API & Integration Tests (`tests/test_orders_api.py`)
* `test_at_risk_orders_endpoint_returns_only_active_at_risk()`:
  * Verifies endpoint returns only the 3 expected at-risk orders (`FE-48291`, `FE-48293`, `FE-48297`).
  * Verifies descending sorting by `estimated_delay_minutes` (18m, then 14m, then 10m).
* `test_at_risk_orders_endpoint_excludes_delivered_and_cancelled()`:
  * Verifies `FE-48294` (delivered, +19m) and `FE-48296` (cancelled, +21m) are not included.
* `test_order_detail_returns_complete_fields()`:
  * Verifies all expected fields (`restaurant_status`, `driver_status`, `support_opened`, `previous_intervention`) are returned.
* `test_backward_compatibility_of_all_orders_endpoint()`:
  * Verifies `GET /api/orders` still returns all 8 orders.

---

## 6. Implementation Sequence

```text
Step 1: Backend Service Layer
  └── Update backend/services/orders.py with get_at_risk_orders() using is_at_risk()

Step 2: API Route Layer
  └── Add @app.get("/api/orders/at-risk") to backend/api.py

Step 3: Test Automation
  └── Add tests in tests/test_orders_api.py and run full test suite

Step 4: Frontend Development
  ├── Update frontend/index.html (table structure, empty state, detail drawer)
  ├── Update frontend/styles.css (dashboard styles, badges, drawer animations)
  └── Update frontend/app.js (data loading, table rendering, detail inspection)

Step 5: End-to-End Verification
  └── Run tests and verify in browser
```
