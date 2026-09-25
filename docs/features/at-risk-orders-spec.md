# At-Risk Orders Queue: Feature Spec

## Goal

Help an Operations Manager find active orders that need review and inspect their existing details.

## Acceptance criteria

- The queue includes only orders accepted by the existing `is_at_risk` rule: ACTIVE, known estimated delay, and delay at least 10 minutes.
- Queue entries are sorted by estimated delay descending.
- Selecting an entry fetches and displays the existing order fields from `/api/orders/<order_id>`.
- A missing order is presented as a readable not-found state with a Close action; other failures are also readable.
- An empty queue has a useful message, and queue cards have their own class and click listener.
- Existing order endpoints and fields remain unchanged; no synthetic risk fields are added.

## Out of scope

Driver reassignment, refunds, maps, predictive scoring, and redesigning the broader operations application.

## Clarifications from repository inspection

`backend/services/risk.py` defines the business threshold and exclusions. `GET /api/orders/<order_id>` already returns the order object or `{"error":"order_not_found"}` with 404. Detail fields are the current JSON contract: order ID, status, promised/current ETA, estimated delay, restaurant/driver status, support opened, and previous intervention.
