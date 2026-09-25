# At-Risk Orders Queue Functional Specification

## User

Operations Manager monitoring live deliveries during a busy service period.

## Goal

Help Operations quickly identify active orders that may require intervention now,
starting with the most urgent orders and allowing an order to be inspected using
the existing order-detail capability.

## Existing Business Rule

An order is actionable risk when all of the following are true:

- `status` is `ACTIVE`.
- `estimated_delay_minutes` is known.
- `estimated_delay_minutes` is at least `10`.

Completed or cancelled orders, orders with unknown delay, and orders delayed by
less than 10 minutes must not appear in the queue.

## Acceptance Criteria

- The application displays a queue of at-risk active orders.
- The queue contains only orders accepted by the existing `is_at_risk()` rule.
- Orders are ordered from highest `estimated_delay_minutes` to lowest.
- Each queue item shows enough existing order information for Operations to
  decide which order to inspect next, including the order ID and delay.
- Selecting a queue item reuses the existing order-detail capability and shows
  the selected order's current details.
- When no orders meet the rule, the application displays a useful empty state
  instead of an empty or broken layout.
- Existing `GET /api/orders` and `GET /api/orders/<order_id>` behavior remains
  unchanged.
- No risk score is introduced as part of this feature.
- Automated tests cover filtering, the 10-minute boundary, descending urgency,
  exclusion of completed/cancelled orders, unknown delays, and the empty state
  or empty response behavior.
- Automated API tests use isolated test-owned data and do not depend on
  `backend/data/orders.json` or production order IDs.

## Out Of Scope

- Driver reassignment.
- Refunds or compensation workflows.
- Maps or live location tracking.
- Predictive models or new risk scoring.
- Recalculating delay from timestamps.
- Changes to customer-facing workflows.
- Database or persistence-layer introduction.
- Editing orders from the queue.

## MVP Decisions

- The queue uses `GET /api/orders/at-risk`.
- The endpoint returns complete existing order objects without a `risk_score`.
- Results are sorted by descending delay, preserving input order for ties.
- Selecting an item fetches the existing order-detail endpoint and renders the
  returned details in the page.
- The queue loads on page load and does not automatically refresh.

## Deferred Questions

- Should the queue refresh automatically during a service period, or only when
  the page is loaded or manually refreshed?
- Should the queue eventually use a narrower response schema?
- Are additional existing fields needed for operational review?