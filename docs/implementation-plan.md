# Implementation Plan

1. Reuse `is_at_risk` in the order service to filter loaded records and sort by delay descending.
2. Add `GET /api/orders/at-risk`; preserve `/api/orders` and existing detail route contracts.
3. Replace the general list view with a compact queue and dedicated detail panel. Fetch details on selection and render all values as text.
4. Handle 404, network/server failures, loading, empty queue, and close actions.
5. Add behavior-oriented endpoint tests, inspect the diff, and run the suite.

## Assumptions checked

- At-risk criteria are not inferred from labels or UI: the centralized service predicate owns them.
- Existing detail endpoint provides all requested fields, so no new detail API is needed.
- Stable ordering among equal delays is not otherwise specified; Python's stable sort preserves source order for ties.
