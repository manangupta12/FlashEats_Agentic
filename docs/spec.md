# Feature Specification: At-Risk Orders Dashboard (V1)

This specification defines the requirements, goals, acceptance criteria, and boundaries for the **At-Risk Orders Dashboard**, designed for FlashEats Operations and Customer Support Agents.

---

## 1) User Specification (Requirements)

### UI & UX Requirements
* **Layout & Primary View:** A clean, focused dashboard view designed for fast triage during peak service periods.
* **At-Risk Orders Table:** The central component is an interactive data table displaying only actionable orders classified as at-risk by the service rule in `is_at_risk()`.
* **Urgency Ordering:** Orders must be sorted in descending order of urgency (highest `estimated_delay_minutes` at the top).
* **Empty State:** When no active orders are at risk, the dashboard must render an explicit, clear empty state (e.g., *"No at-risk orders requiring intervention at this time"*).
* **5 Essential Table Columns:**
  1. **Order ID:** Unique identifier for the order (e.g., `FE-48291`).
  2. **Promised & Current ETA:** Baseline promised time vs. updated projection (e.g., `19:42 → 20:00`).
  3. **Estimated Delay:** Key quantitative risk metric in minutes (e.g., `+18 min`), highlighted visually.
  4. **Fulfillment Status:** Combined operational status showing restaurant and driver progress (e.g., `Restaurant: READY | Driver: 1.8 km away`).
  5. **Support / Intervention Status:** Indicator showing if support is already opened or previous interventions logged (e.g., `Support: Open | Prev: ETA_MESSAGE`), plus an "Inspect" action trigger.
* **Row Interaction & Detail View:**
  * Clicking on an order row expands an inline detail drawer/panel (or opens a detailed inspection view).
  * The detail view retrieves full order context via `GET /api/orders/<order_id>` and displays:
    * Complete lifecycle state (`status`, `restaurant_status`, `driver_status`).
    * Full timing details (`promised_eta`, `current_eta`, `estimated_delay_minutes`).
    * Intervention and ticket history (`support_opened`, `previous_intervention`).

---

## 2) Goal

### Business Objectives
* **Proactive Delay Mitigation:** Enable operations and support agents to intervene before customers experience severe SLA breaches or file complaints.
* **Reduce Inbound Support Volume:** Deflect reactive customer support tickets by addressing delivery bottlenecks early.
* **Improve Customer Retention & CSAT:** Maintain trust during peak delivery windows through timely, accurate operational handling.

### User Goals (Support & Operations Agents)
* **Instant Risk Visibility:** Triage and pinpoint high-risk orders without manually parsing through hundreds of on-time or completed deliveries.
* **Actionable Context at a Glance:** Access all necessary fulfillment context (restaurant status, driver distance/status, past interventions) in a single click to determine the next intervention.

---

## 3) Acceptance Criteria

### Backend & Business Logic
* [ ] **Risk Filtering Rule:** Only orders where `status == "ACTIVE"` AND `estimated_delay_minutes is not None` AND `estimated_delay_minutes >= 10` are returned in the at-risk queue.
* [ ] **Exclusion Rules:** Orders with `status` in `['DELIVERED', 'CANCELLED']` or with `estimated_delay_minutes == None` must **never** appear in the at-risk list, regardless of prior delay values.
* [ ] **API Contract Stability:** Existing contracts for `GET /api/orders` and `GET /api/orders/<order_id>` remain backward-compatible without introducing synthetic fields (e.g., no raw `risk_score` fields).

### Frontend & UX
* [ ] **Prioritized Sorting:** Orders in the table are sorted strictly descending by `estimated_delay_minutes` (highest delay first).
* [ ] **Table Display:** The table displays exactly the 5 specified columns with valid data mapped from `backend/models.py`.
* [ ] **Detail Inspection:** Clicking any order row fetches and displays full order metadata (restaurant status, driver status, support opened flag, previous intervention) without page reloads or raw `alert()` dialogs.
* [ ] **Empty State Handling:** When zero orders qualify as at-risk, a dedicated empty-state banner/message is rendered instead of a blank table or broken loading state.
* [ ] **Error Handling:** Failed network requests to `/api/orders` display a user-friendly error message.

### Testing & Quality Assurance
* [x] Automated unit tests in `tests/test_risk.py` pass for all threshold edge cases (9 min, 10 min, 11 min, null, completed/DELIVERED, and CANCELLED).
* [x] API integration tests in `tests/test_orders_api.py` verify correct order filtering, descending urgency sorting, and detail retrieval.


---

## 4) Out of Scope (V1)

The following capabilities are explicitly deferred from the V1 release to maintain a minimal, verifiable implementation:

1. **Automated Driver Reassignment / Dispatching:** No automated or manual re-dispatching of couriers from the dashboard.
2. **Refund & Compensation Processing:** In-app refund creation, voucher generation, or payment gateway interactions.
3. **Live GPS Map Visualization:** Embedding interactive map widgets, live driver coordinate tracking, or route polylines.
4. **Predictive Machine Learning Risk Models:** Replacing the current heuristic rule (`estimated_delay_minutes >= 10`) with ML scoring or external traffic prediction APIs.

---

## 5) Open Questions

1. **Schema Field Availability (Restaurant Name):** The current `Order` model and `orders.json` contain `restaurant_status` (e.g., `READY`, `PREPARING`), but no `restaurant_name` string. Should the column present `restaurant_status` / fulfillment state, or will restaurant naming metadata be added to the data source in a later version?
2. **API Endpoint Strategy:** Should at-risk orders be served via:
   * A dedicated endpoint (e.g., `GET /api/orders/at-risk`), or
   * A query parameter on the existing list endpoint (e.g., `GET /api/orders?at_risk=true`), or
   * Frontend filtering of the existing `GET /api/orders` payload using the shared rule?
   *(Note: A dedicated service method/endpoint aligns best with `docs/architecture.md` boundary principles).*
3. **Tie-Breaking Sort Order:** When multiple at-risk orders have the exact same `estimated_delay_minutes` (e.g., two orders with +10 min delay), what is the secondary sorting criterion (e.g., earliest `promised_eta` first vs. `order_id`)?
4. **Detail View Presentation Pattern:** Should order details expand directly inside the table row as an accordion, or open in a side inspection drawer beside the table?
