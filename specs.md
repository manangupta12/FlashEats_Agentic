# Feature Specification: At-Risk Orders Queue

## 1. User
* **Primary Persona**: Operations Manager / Dispatch Controller.
* **Context**: Monitors live food-delivery operations during busy service periods in the FlashEats Operations Console.

---

## 2. Goal
* **Primary Objective**: Quickly surface active food-delivery orders that require immediate operational review and intervention.
* **Key Requirements**:
  * Filter active orders to display only those exceeding operational risk thresholds (`estimated_delay_minutes >= 10`).
  * Prioritize order queue by operational urgency (highest estimated delay first).
  * Provide key operational details per order card to help the user decide which order to inspect next.
  * Provide a clear, actionable empty state when no orders are at risk.
  * Maintain zero friction by reusing existing order detail capabilities (`/api/orders/<order_id>`).

---

## 3. Acceptance Criteria

* **AC-1 (Service Rule Reuse)**: The backend uses the centralized `is_at_risk()` helper in `backend/services/risk.py` to identify risk.
* **AC-2 (API Endpoint)**: A new route `GET /api/orders/at-risk` returns a JSON list of orders meeting the at-risk criteria (`status == "ACTIVE"` AND `estimated_delay_minutes >= 10`).
* **AC-3 (Exclusion Rules)**: `DELIVERED`, `CANCELLED`, or orders with `null` estimated delay are strictly excluded from the queue (even if previously delayed).
* **AC-4 (Urgency Sorting)**: Orders returned by `GET /api/orders/at-risk` are sorted in **descending order** of `estimated_delay_minutes` (e.g., +18 min delay appears before +14 min delay). Secondary sort order is `promised_eta` ascending.
* **AC-5 (No Synthetic Fields)**: Output order payload preserves the standard `Order` schema in `backend/models.py` without injecting unapproved fields like `risk_score`.
* **AC-6 (Frontend Queue Display & Card Content)**: The frontend fetches `GET /api/orders/at-risk` and renders order cards showing: Order ID, Status, Promised ETA, Estimated Delay, Restaurant Status, Driver Status, and Support Ticket status (`support_opened`).
* **AC-7 (Empty State Rendering)**: When `GET /api/orders/at-risk` returns an empty array `[]`, the UI displays a clear message: *"No active orders currently at risk. All live deliveries are operating within normal parameters."*
* **AC-8 (Card Interaction)**: Clicking an order card in the At-Risk Queue triggers the existing order detail view capability.
* **AC-9 (Regression & Test Coverage)**: All existing 7 pytest tests continue to pass, and new automated unit/API tests are added to verify the `GET /api/orders/at-risk` endpoint and sorting logic.

---

## 4. Test Cases Specification & Verification Matrix

| Test Case ID | Test Target / Function | Condition / Input | Expected Result | Automated Test Location |
| :--- | :--- | :--- | :--- | :--- |
| **TC-1** | Active Risky Order Inclusion | `status: "ACTIVE"`, `delay: 18` | Included in queue | `test_at_risk_orders_endpoint_returns_filtered_and_sorted_queue` |
| **TC-2** | Completed Order Exclusion | `status: "DELIVERED"`, `delay: 19` | Excluded from queue | `test_completed_and_cancelled_orders_excluded_from_at_risk_endpoint` |
| **TC-3** | Cancelled Order Exclusion | `status: "CANCELLED"`, `delay: 21` | Excluded from queue | `test_completed_and_cancelled_orders_excluded_from_at_risk_endpoint` |
| **TC-4** | Unknown Delay Exclusion | `status: "ACTIVE"`, `delay: None` | Excluded from queue | `test_unknown_delay_orders_excluded_from_at_risk_endpoint` |
| **TC-5** | Exact Threshold Boundary | `status: "ACTIVE"`, `delay: 10` | Included in queue | `test_delay_exactly_10_minutes_included_in_at_risk_endpoint` |
| **TC-6** | Below Threshold Boundary | `status: "ACTIVE"`, `delay: 9` | Excluded from queue | `test_active_order_below_threshold_is_not_at_risk` |
| **TC-7** | Urgency Sort Order | Delays: `[10, 18, 14]` | Output sorted `[18, 14, 10]` | `test_at_risk_endpoint_results_sorted_by_delay_descending` |
| **TC-8** | Base API Contract Integrity | `GET /api/orders` | Returns all 8 orders unmodified | `test_orders_endpoint_returns_existing_orders` |
| **TC-9** | Order Detail 404 Behavior | `GET /api/orders/FE-DOES-NOT-EXIST` | Returns HTTP 404 with error message | `test_order_detail_returns_404_for_unknown_order` |
| **TC-10** | Schema Field Protection | Output JSON objects | `risk_score` absent, `estimated_delay_minutes` present | `test_existing_api_does_not_expose_risk_score_field` |

---

## 5. Risks & Mitigation Matrix

| Risk ID | Identified Risk Description | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **R-1** | **Stale/Unknown Delays Misclassified**: Orders with uncalculated delay (`null`) might be converted into numeric zero or trigger false alerts. | High | Enforced strict `delay is not None` checks in central `is_at_risk()` service helper. Verified by `TC-4`. |
| **R-2** | **Historical Order Pollution**: Delivered or Cancelled late orders polluting the operational intervention queue. | High | Enforced strict `status == "ACTIVE"` requirement in risk rule. Verified by `TC-2` and `TC-3`. |
| **R-3** | **API Contract Pollution / Breaking Changes**: Adding synthetic fields (e.g. `risk_score`) breaks consumers relying on clean `Order` TypedDict. | Medium | Enforced standard `Order` schema without extra calculated fields. Verified by `TC-10`. |
| **R-4** | **Existing Consumer Regression**: Modifying original `/api/orders` route alters list ordering or length for existing tools. | High | Introduced dedicated `@app.get("/api/orders/at-risk")` route, leaving `GET /api/orders` completely untouched. Verified by `TC-8`. |

---

## 6. Out of Scope

To prevent scope creep and adhere to product constraints (`docs/product_context.md`):

* ❌ **Driver Reassignment**: Automated or manual driver re-dispatch / re-assignment workflows.
* ❌ **Financial Actions**: Issuing customer refunds, discount vouchers, or order cancellation actions.
* ❌ **Visual Mapping**: Map renderings, GPS driver route tracking, or visual geofencing.
* ❌ **Predictive Models**: Modifying delay calculation algorithms or changing the 10-minute risk threshold.
* ❌ **Architecture Changes**: Introducing database systems, ORMs, websockets, backend queues, or third-party frontend frameworks.

---

## 7. Open Questions & Resolved Standards

1. **Tie-Breaker Rule**: Secondary sort is defined as `promised_eta` ascending (earlier promised delivery time first).
2. **UI Navigation**: Rendered as a dedicated "At-Risk Orders Queue" section with live count badge directly above the "All Active Orders" section.
