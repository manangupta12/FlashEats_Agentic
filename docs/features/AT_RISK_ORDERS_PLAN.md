# Implementation Plan — At-Risk Orders Queue

Derived from [at-risk-orders-spec.md](at-risk-orders-spec.md) (what/why) and [at-risk-orders-technical-spec.md](at-risk-orders-technical-spec.md) (how). Executed one task at a time, per [AGENT_TASK.md](../../AGENT_TASK.md): implement, diff review, tests, before moving to the next task.

## Task 1 — `get_at_risk_orders` in `risk.py`

- Add `get_at_risk_orders(orders: list[dict]) -> list[dict]` to `backend/services/risk.py`.
- Filters with existing `is_at_risk`, sorts by `estimated_delay_minutes` descending, stable on ties.
- No other file touched.

**Verify:** add the unit tests from technical-spec §4 to `tests/test_risk.py` and run `pytest tests/test_risk.py -q`.

## Task 2 — `GET /api/at-risk-orders` route

- Add the route in `backend/api.py`: load orders, call `get_at_risk_orders`, return JSON.
- Confirm route ordering doesn't clash with `/api/orders/<order_id>`.
- No other file touched.

**Verify:** add the API tests from technical-spec §4 to `tests/test_orders_api.py`, run the full suite (`pytest -q`) to confirm existing `/api/orders` and `/api/orders/<id>` tests still pass unmodified.

## Task 3 — Frontend queue section

- `index.html`: add the queue container + its own message element.
- `app.js`: add `loadAtRiskQueue()` — fetch, render cards, empty state, reuse existing click-through.
- `styles.css`: minimal styling reusing existing classes.

**Verify:** manual run (`python app.py`), load `http://127.0.0.1:5000`, confirm queue shows FE-48291, FE-48293, FE-48297 in that order, and confirm empty state renders if the data is temporarily edited to have none at risk (then revert).

## Task 4 — Full regression pass

- Run `pytest -q` for the whole suite.
- Re-check acceptance criteria in [at-risk-orders-spec.md](at-risk-orders-spec.md) §3 one by one against the running app.

## Sequencing notes

- Tasks 1 and 2 are backend-only and independently testable without the frontend; do these first.
- Task 3 depends on Task 2's route existing.
- Do not start Task 3 until Task 2's tests pass — the frontend has nothing to call otherwise.

## Deferred / not started until confirmed

- Tie-break rule for equal delays (technical-spec §6) — defaults to stable sort unless Operations specifies otherwise; revisit before calling Task 1 final if that answer arrives first.
- Whether the detail click-through gets upgraded beyond the current `alert()` — out of scope for Task 3 unless explicitly requested.