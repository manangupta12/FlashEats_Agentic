# Feature Spec — At-Risk Orders Queue

Refines `docs/features/at-risk-orders-starter.md` after inspecting the repository.

## User and goal

**User:** Operations Manager during a busy service period.

**Goal:** Quickly see which active orders need review now, most urgent first, and open one to inspect it.

## Business rule (reused, not redefined)

An order belongs in the queue **if and only if** `backend.services.risk.is_at_risk(order)` returns `True`:

- `status == "ACTIVE"`, and
- `estimated_delay_minutes` is known (not `null`), and
- `estimated_delay_minutes >= 10`.

The queue must call `is_at_risk`. It must not re-implement the threshold, the status check or the null handling anywhere else (backend or frontend).

Product copy uses "late", "delayed" and "at risk" loosely. In this feature they all mean the rule above.

## Decisions on ambiguities

| # | Ambiguity | Decision | Rationale |
|---|---|---|---|
| D1 | What "most urgent first" means | Sort by `estimated_delay_minutes` **descending**, then `promised_eta` **ascending**, then `order_id` **ascending** | Delay is the only urgency signal the existing rule uses. The tie-breaks make the order deterministic. |
| D2 | Orders with unknown delay (e.g. FE-48295) | **Excluded** from the queue | The existing rule doesn't classify them as at risk, and the product context says unknown delay must not be turned into a number. |
| D3 | Changing the existing `/api/orders` | **No change.** Add a new endpoint | Existing contracts must stay stable, and the tests expect `/api/orders` to return all 8 orders. |
| D4 | Adding a score/urgency field | **No** new fields (no `risk_score`, no `is_at_risk` flag) | The tests assert `risk_score` is absent, and the request says "do not invent missing fields". |
| D5 | "Reuse the existing order-detail capability" | Selecting a queue item calls the existing `GET /api/orders/<order_id>` and shows the result in a detail panel on the page | The backend endpoint already exists. The UI has no detail view yet, only an `alert`. |
| D6 | `promised_eta` format | Treated as a zero-padded same-day `"HH:MM"` string, so string order equals time order | This matches all the seed data. Handling orders across midnight is out of scope. |

## API

### New: `GET /api/at-risk-orders`

- `200 OK` with a JSON **array** of order objects.
- Each element has **exactly the same shape** as an element of `GET /api/orders`, with no added or removed fields.
- It contains only orders where `is_at_risk(order)` is `True`, sorted as in D1.
- If no orders qualify it returns `[]` with `200` (not `404`).

The path is `/api/at-risk-orders` and not `/api/orders/at-risk`, so it can't be confused with the `/api/orders/<order_id>` route.

### Unchanged

- `GET /api/orders` still returns all orders, in file order.
- `GET /api/orders/<order_id>` still returns the order, or `404 {"error": "order_not_found"}`.

## UI

Add an **"At-risk orders"** section above the existing order list on the current page.

Each queue item shows:

- `order_id`
- delay, e.g. `18 min late`
- promised ETA and current ETA
- restaurant status and driver status
- whether support is opened
- previous intervention, or "None"

States:

- **Loading:** "Loading at-risk orders…"
- **Empty:** "No active orders are at risk right now (delay of 10+ minutes)."
- **Error:** "Could not load at-risk orders: <reason>". This must not break the existing list.

Selecting an item fetches `GET /api/orders/<order_id>` and shows its fields in a detail panel. If that fetch fails, the panel shows an error message.

The existing "Active Orders" list keeps its current behavior.

Order data is inserted into the page escaped, not as raw HTML.

## Acceptance criteria

With the current `backend/data/orders.json`:

1. `GET /api/at-risk-orders` returns exactly `FE-48291` (18), `FE-48293` (14) and `FE-48297` (10), in that order.
2. FE-48297 is included: the threshold is inclusive (10 ≥ 10).
3. FE-48292 (6 min) and FE-48298 (−3 min) are excluded because they are below the threshold.
4. FE-48295 (`null` delay) is excluded.
5. FE-48294 (`DELIVERED`, 19 min) and FE-48296 (`CANCELLED`, 21 min) are excluded, even though their delay is high.
6. No element of the response has a `risk_score` field, and each element's keys equal the keys of the same order in `/api/orders`.
7. With no qualifying orders, the endpoint returns `200 []` and the UI shows the empty state.
8. Ties on delay are ordered by earlier `promised_eta`, then `order_id`.
9. The existing tests in `tests/` pass unchanged.
10. Clicking a queue item shows that order's detail, fetched from `/api/orders/<order_id>`.
11. The frontend never reads `backend/data/orders.json` directly and never re-implements the risk rule.

## Out of scope

- Driver reassignment, refunds, maps, predictive or ETA-model changes.
- A database, a frontend framework, a message queue or a new service.
- Changing the risk threshold or the rule.
- A separate "unknown delay" queue (see open questions).
- Auto-refresh or polling, authentication, pagination.
- Sorting across midnight or date-aware ETAs.
- Changing click behavior in the existing all-orders list.

## Open questions for Product

1. Should active orders with unknown delay (e.g. FE-48295, driver `SEARCHING`) appear in a separate "needs a check" group, without a numeric risk value?
2. Should `support_opened` or `previous_intervention` affect urgency ordering?
3. Is manual page refresh enough, or does Operations need auto-refresh?
