# At-Risk Orders Queue: Implementation Summary

This document serves as a comprehensive summary and evidence of the steps taken to implement the **At-Risk Orders Queue** backend feature.

## 1. Repository Inspection & Planning
- **Inspection**: Analyzed the existing architecture (`backend/api.py`, `backend/services/risk.py`), UI, and JSON data without making any code changes.
- **Functional Spec**: Drafted `FunctionalSpec.md` outlining the user experience, acceptance criteria, and explicitly confirming the reuse of the existing `is_at_risk()` business logic.
- **Technical Spec**: Drafted `TechnicalSpec.md` breaking the feature down into a verifiable execution plan, avoiding broad changes (like building the whole dashboard at once).

## 2. Backend Implementation (Task 1)
Instead of a massive PR, we started with a small, reversible backend change:
- **`backend/services/orders.py`**: Created `get_at_risk_orders()` which pulls all orders, applies the centralized `is_at_risk` rule, and sorts the results descending by `estimated_delay_minutes`.
- **`backend/api.py`**: Added the new route `@app.get("/api/orders/at-risk")`. 
  - *Critical Catch*: This route was intentionally placed *above* the `@app.get("/api/orders/<order_id>")` route so that "at-risk" wouldn't be mistakenly swallowed as an order ID parameter by Flask.

## 3. Pre-existing Bug Fix
- **Issue**: Running tests locally immediately crashed with `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`.
- **Resolution**: Identified this as a Python 3.9 type-hint incompatibility inside the starter code (`dict | None`). Refactored line 15 of `backend/services/orders.py` to use `typing.Optional[dict]`, allowing tests to execute successfully.

## 4. Behavioral Testing (Task 2) & Refactoring
- **Initial Implementation**: Added `test_at_risk_orders_endpoint` to `tests/test_orders_api.py` to verify the endpoint successfully returned a 200 status and the correct orders. 
- **User Intervention (Catching a Risky Assumption)**: The initial test passed but relied on hardcoded data (e.g., asserting that `FE-48291` was at index 0). The user correctly identified this as a fragile code smell since changes to `orders.json` would break the test.
- **Dynamic Refactoring**: The test was completely rewritten to be dynamic. It now fetches the full order list, dynamically computes how many orders *should* meet the risk criteria, and loops through the at-risk payload asserting that every single item respects the `ACTIVE` state, the `>= 10` minute threshold, and the descending sort order. All 8 tests passed in the virtual environment.
