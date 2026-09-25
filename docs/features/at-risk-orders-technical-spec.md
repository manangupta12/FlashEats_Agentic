# At-Risk Orders Queue Technical Spec

## Current Context

The backend is Flask and the frontend is static HTML/CSS/JS.
Orders are loaded from `backend/data/orders.json` via
`backend/services/orders.py`. The risk predicate in
`backend/services/risk.py` remains the single source of truth.

## Implemented Request Path

```text
Queue UI
  -> GET /api/orders/at-risk
  -> orders service
  -> is_at_risk(order)
  -> file-based orders source
```

Order selection keeps the existing detail path:

```text
Queue item click
  -> GET /api/orders/<order_id>
  -> existing order detail payload
```

## API Contract

New route:

```text
GET /api/orders/at-risk
```

Returns a JSON array of existing order objects. Each returned order satisfies
`is_at_risk(order)`. No `risk_score` field is added.

If there are no matches, return HTTP `200` with `[]`.

Existing routes stay unchanged:

- `GET /api/orders` returns all orders
- `GET /api/orders/<order_id>` returns one order or existing `404` body

## Service Behavior

The queue service function:

1. Loads all orders using the existing loader
2. Filters with `is_at_risk(order)`
3. Sorts by `estimated_delay_minutes` descending
4. Keeps original order when delays tie

No rule duplication in API routes or frontend logic.

## Frontend Behavior

Frontend updates include:

- Fetch at-risk queue on page load
- Render queue in urgency order
- Show order ID and delay, along with existing useful fields
- Fetch and render detail data after selecting any card
- Show loading, empty, and error messages for queue and detail states

No frontend framework or persistence-layer additions are required.

## Test Coverage Expectations

API tests should validate:

- At-risk filtering based on business rules
- Descending delay order
- Inclusive threshold at 10 minutes
- Exclusion of delivered, cancelled, and unknown-delay cases
- Empty output as `200` plus `[]`
- No contract regression on existing list/detail endpoints

Risk tests should validate:

- Threshold boundaries
- Missing or unknown delay handling
- Non-active statuses

API tests must use temporary test fixture data and not read production records.
