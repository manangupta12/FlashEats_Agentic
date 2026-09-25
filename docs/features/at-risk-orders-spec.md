# At-Risk Orders Queue Specification (Functional)

## User
Operations Manager

## Goal
Quickly identify active orders that require review during a busy service period.

## Acceptance Criteria
- **Show risky active orders**: The UI must display a queue of orders that are at risk.
- **Risk classification**: Must use the existing business rule for risk.
  - Exactly 10 minutes of estimated delay is considered at risk (inclusive threshold).
  - Unknown delay (`null`) is excluded from the risk queue.
  - Non-active orders (e.g., DELIVERED, CANCELLED) are excluded.
- **Ordering**: Put the most urgent orders (highest estimated delay) first.
- **Order Details**: Show enough information on the queue cards to decide which order to inspect next (e.g., order ID, delay, restaurant status, driver status).
- **Navigation**: Selecting an order should reuse the existing order-detail capability.
- **Empty State**: Provide a useful empty state when there are no at-risk orders.

## Out of Scope
- Driver reassignment, refunds, maps, or predictive-model work are explicitly out of scope for the MVP.
- Modifying the core business risk logic.

## Open Questions
- **Selecting an order**: Does "reuse the existing order-detail capability" mean keeping the current `window.alert()` placeholder, or building a proper detail view?
- **Urgency definition**: Is "most urgent" defined purely by the highest `estimated_delay_minutes`?
- **Empty state copy**: What should the exact wording for the empty state be?
