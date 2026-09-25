# At-Risk Orders Queue Technical Specification

## Technical Context

The application is a Flask backend with a static frontend. Orders are read
from `backend/data/orders.json` through
`backend/services/orders.py`. The existing risk rule is implemented by
`backend/services/risk.py` and must remain the single source of truth.

## Implemented Request Flow

```text
Frontend queue
  -> at-risk orders API
  -> orders service
  -> is_at_risk(order)
  -> file-backed order source
```

Selecting an item should continue to use the existing order-detail endpoint:

```text
Selected queue item
  -> GET /api/orders/<order_id>
  -> existing order detail response
```

## API Contract

A dedicated read-only endpoint is implemented for the queue:

```text
GET /api/orders/at-risk
```

The response should be a JSON array of existing order objects. Each returned
order must satisfy `is_at_risk(order)` and must retain its existing fields.
Do not add a `risk_score` field.

The endpoint should return HTTP `200` with an empty JSON array when no orders
are at risk. Existing endpoints must keep their current behavior:

- `GET /api/orders` continues to return all orders.
- `GET /api/orders/<order_id>` continues to return one order or the existing
  `404` error response.

## Implemented Service Behavior

The service-level queue function:

1. Loads orders using the existing file-backed loader.
2. Filters orders by calling `is_at_risk(order)`.
3. Sorts results by `estimated_delay_minutes` descending.
4. Preserves the existing JSON order for equal delays unless a later product
   decision specifies a secondary sort.

Do not duplicate the risk predicate in the API route or frontend.

## Implemented Frontend Behavior

The frontend should:

- Request the at-risk orders endpoint on page load.
- Render the returned orders in urgency order.
- Show each order ID and delay, plus other existing fields needed for review.
- Use the existing order-detail endpoint when an order is selected.
- Render a useful empty state for an empty array.
- Render a useful error state if the queue request fails.

No frontend framework or new persistence layer is required.

## Test Coverage

API tests cover:

- Only at-risk active orders being returned.
- Descending delay order.
- The inclusive 10-minute threshold.
- Exclusion of delivered, cancelled, and unknown-delay orders.
- An empty result returning HTTP `200` and `[]`.
- Existing order-list and order-detail contracts remaining unchanged.

Risk tests cover the predicate independently, including boundaries, missing
fields, unknown delays, and non-active statuses.

All API tests use temporary test-owned data through the shared test client
fixture. Tests must not read `backend/data/orders.json`, assert production
order IDs, or depend on production record counts. Test data should be created
only to exercise a behavior under test.

## Likely File Changes

Implemented files:

- `backend/api.py`: queue route.
- `backend/services/orders.py`: filtered and sorted queue data.
- `frontend/app.js`: queue and detail behavior.
- `frontend/index.html`: queue and detail containers.
- `frontend/styles.css`: queue, empty, and error states.
- `tests/conftest.py`: isolated temporary API data fixture.
- `tests/test_orders_api.py`: queue contract tests.
- `tests/test_risk.py`: boundary and exclusion tests.