# Functional Spec — At-Risk Orders Queue

Status: draft
Source request: `docs/features/at-risk-orders-starter.md`
Product constraints: `docs/product_context.md`

## User

Operations Manager monitoring live deliveries during a busy service period.

## Goal

Quickly see the active orders that may need intervention **now**, most urgent first,
with enough context on each row to decide which order to open next.

## Background — the rule already exists

`backend/services/risk.py::is_at_risk` already encodes the business rule Operations uses.
This feature **surfaces** that rule; it does not define a new one.

```python
order["status"] == "ACTIVE"
and order["estimated_delay_minutes"] is not None
and order["estimated_delay_minutes"] >= 10
```

Product language ("late", "delayed", "at risk") is used loosely in the request documents.
The implemented rule is authoritative.

## Acceptance criteria

1. **Risk uses the existing service rule.** The queue is produced by calling
   `backend.services.risk.is_at_risk`. The rule is not re-implemented, copied, or inlined
   anywhere else.
2. **Exactly 10 minutes is included.** An ACTIVE order with
   `estimated_delay_minutes == 10` appears in the queue (threshold is `>=`, not `>`).
3. **Unknown delay is excluded.** An ACTIVE order with
   `estimated_delay_minutes == null` does not appear, and is never coerced to `0`
   or any other numeric stand-in.
4. **Delivered and cancelled are excluded.** An order whose status is not `ACTIVE`
   never appears, even when its delay is large (e.g. a `DELIVERED` order at 19 min,
   a `CANCELLED` order at 21 min).
5. **Most urgent first.** The queue is sorted by `estimated_delay_minutes`
   descending. Ties keep the source order (stable sort).
6. **Endpoint follows the existing route hierarchy.** The queue is served from
   `GET /api/orders/at-risk` — a sub-resource of the `/api/orders` collection,
   matching every other API route. A sibling top-level path such as
   `/api/at-risk-orders` is explicitly rejected. The static segment must resolve
   ahead of `/api/orders/<order_id>` and must never be handled as an order id.
7. **Frontend uses the backend API.** The UI reads the queue from the backend
   endpoint. It does not read `backend/data/orders.json` directly and does not
   re-filter or re-rank orders client-side.
8. **Existing contracts unchanged.** `GET /api/orders` and `GET /api/orders/<id>`
   keep their current shape and status codes. No new field (e.g. `risk_score`)
   is added to the order payload.
9. **Row content.** Each row shows `order_id`, `status`, `promised_eta`,
   `current_eta`, `estimated_delay_minutes`, `restaurant_status`, `driver_status` —
   all existing fields only. No invented fields.
10. **Selecting an order reuses order detail.** Selecting a row uses the existing
   `GET /api/orders/<order_id>` capability; no new detail endpoint.
11. **States.** The UI has a loading state, an explicit empty state
    ("No orders currently at risk"), and an error state when the request fails.

## Testing strategy

Behavior is verified against **controlled fixtures**, never against the contents of
`backend/data/orders.json`. Each test supplies the orders its own case needs by
substituting the service-layer data source, so:

- a test states its premise inline and is readable on its own,
- editing the sample data cannot break unrelated tests,
- an assertion proves the rule rather than the current contents of a file.

This mirrors the `make_order(**overrides)` factory already used by `tests/test_risk.py`.

## Out of scope (MVP)

- Driver reassignment.
- Refunds.
- Maps / geolocation.
- Predictive-model or risk-score changes.
- Changing the risk threshold or adding new risk signals
  (`support_opened`, `previous_intervention`, `restaurant_status` are **displayed**,
  not used as risk inputs).
- Persistence, a database, a frontend framework, auth, pagination, real-time push.

## Open questions

1. **Negative delay.** `FE-48298` has `estimated_delay_minutes: -3` (running early).
   The existing rule already excludes it (`-3 >= 10` is false). Assumed correct; no
   special handling. Confirm with Operations.
2. **Tie-break.** Two orders with equal delay — is there a preferred secondary sort
   (e.g. `support_opened` first, or earliest `promised_eta`)? Assumed: stable source order.
3. **Other active-like statuses.** Only `ACTIVE`, `DELIVERED`, `CANCELLED` appear in the
   sample data. If a future status (e.g. `PENDING`) is introduced, is it actionable?
   Assumed: only `ACTIVE`, per the existing rule.
4. **Refresh cadence.** Is manual page load enough for the MVP, or is polling expected?
   Assumed: load on page open only.
