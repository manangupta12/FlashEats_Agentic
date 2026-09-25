# Functional Spec — At-Risk Orders Queue

Refines `docs/features/at-risk-orders-starter.md`.

## User

Operations Manager monitoring live deliveries during a busy service period.

## Goal

Let the Operations Manager see, at a glance, which active orders need intervention now, most urgent first, and inspect any of them without leaving the page.

## Acceptance criteria

### Which orders appear

1. The queue contains exactly the orders that the existing at-risk rule classifies as at risk: status `ACTIVE` and a known estimated delay of 10 minutes or more.
2. The at-risk rule is not redefined or duplicated. The queue uses the existing rule as-is.
3. Delivered and cancelled orders never appear, however late they were.
4. Active orders with an unknown delay do not appear in the queue, and their delay is never shown or treated as a number.
5. Active orders delayed by less than 10 minutes, including orders running early, do not appear.
6. With the current sample data, the queue contains FE-48291, FE-48293 and FE-48297, and nothing else.

### Order

7. Orders are sorted by estimated delay, largest first.
8. Orders with equal delay are sorted by earliest promised ETA, then by order ID, so the order is always the same.
9. With the current sample data, the order is FE-48291 (18 min), FE-48293 (14 min), FE-48297 (10 min).

### What each entry shows

10. Each queue entry shows:
    - order ID
    - estimated delay in minutes
    - promised ETA and current ETA
    - restaurant status and driver status
    - whether a support ticket is open
    - the previous intervention, or a clear "none" when there has not been one
11. Only fields that already exist on an order are shown. No new or derived fields, such as a risk score, are introduced.

### Selecting an order

12. Selecting a queue entry shows that order's full details on the same page, using the existing order-detail capability.
13. If the selected order can no longer be found, the manager sees a clear "order not found" message rather than a broken or blank view.

### Layout and empty state

14. The queue appears above the existing order list on the same page. The existing list is still there and behaves as before.
15. When no orders are at risk, the queue shows a message that states the rule, for example: "No active orders are delayed 10+ minutes right now."
16. If the queue cannot be loaded, the manager sees an error message, which is visibly different from the empty state.
17. The queue loads when the page opens. It does not refresh automatically.

### Compatibility

18. Existing behaviour that consumers depend on does not change:
    - The full order list still returns all orders.
    - Order detail still returns the same fields, with no risk score added.
    - Unknown orders still return the same "not found" response.
19. All existing tests continue to pass without modification.

## Out of scope

- Driver reassignment
- Refunds or compensation
- Maps or driver location views
- Changes to the at-risk rule, its 10-minute threshold, or any predictive model
- Automatic refresh or live updates
- Taking actions on an order from the queue (contacting, messaging, escalating)
- Filtering, searching or configuring the queue
- Any new database, frontend framework, queue system or service

## Open questions

1. **Unknown-delay orders:** Should Operations be able to see, from the queue, the active orders whose delay is unknown (for example FE-48295, driver still searching)? For now they appear only in the main order list.
2. **Tie-break priority:** Should an open support ticket or a previous intervention make an order more urgent than another order with the same delay? For now only the promised ETA is used.
3. **Refresh:** Is loading the queue once, when the page opens, acceptable during a busy service, or does Operations need it to update on its own?
4. **Threshold visibility:** Should the 10-minute threshold be shown permanently on the queue, or only in the empty state?
5. **Driver status format:** Driver status mixes status codes (`ASSIGNED`) with free text (`1.8 km away`). Should the queue show it as-is?
