# At-Risk Orders Queue Functional Spec

## User

Operations Manager supervising live deliveries in a busy window.

## Goal

Surface active orders that likely need intervention, starting with the highest
delay, and let Operations inspect each order with the current detail flow.

## Rule To Reuse

An order is treated as at-risk only when all conditions hold:

- `status` equals `ACTIVE`
- `estimated_delay_minutes` is present
- `estimated_delay_minutes` is `>= 10`

Delivered and cancelled orders are excluded. Orders with unknown delay are also
excluded. Delays below 10 minutes are excluded.

## Acceptance Criteria

- The app shows a queue for at-risk active orders.
- Queue contents are based on the existing `is_at_risk()` rule.
- Queue order is descending by `estimated_delay_minutes`.
- Each row shows existing order data including order ID and delay.
- Selecting a row shows the order using the existing order-detail behavior.
- Empty matches produce a clear empty state, not a blank UI.
- Existing `GET /api/orders` and `GET /api/orders/<order_id>` behavior is unchanged.
- No `risk_score` field is introduced.
- Automated tests cover filtering, threshold boundaries, sorting, status exclusions,
  unknown delays, and empty output behavior.
- API tests use isolated fixture data and do not rely on `backend/data/orders.json`
  content or production IDs.

## Out Of Scope

- Driver reassignment
- Refund flows
- Map and location tracking
- Predictive models and new risk scoring
- Delay recomputation from timestamps
- Customer-side workflow changes
- Database introduction
- Editing orders from the queue

## MVP Choices

- Queue endpoint: `GET /api/orders/at-risk`
- Response shape: existing full order objects
- Sorting: descending `estimated_delay_minutes`, stable for ties
- Detail interaction: keep using `GET /api/orders/<order_id>`
- Load behavior: fetch queue on page load, no auto-refresh yet

## Open Product Questions

- Should this queue auto-refresh during service?
- Should the endpoint later return a smaller schema?
- Are more existing fields needed for faster operator decisions?
