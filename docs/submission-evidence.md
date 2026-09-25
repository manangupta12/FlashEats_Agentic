# Agentic Coding Challenge Evidence

## Repository inspection prompt

“Inspect the repository without modifying files. Identify the architecture, relevant business rules, tests, APIs, and ambiguities for the At-Risk Orders Queue.”

## Final feature spec

See [features/at-risk-orders-spec.md](features/at-risk-orders-spec.md). It captures the existing risk rule, queue/detail acceptance criteria, contract constraints, and out-of-scope work.

## Implementation plan

See [implementation-plan.md](implementation-plan.md). Work was split into service/API, UI interaction, and focused regression coverage.

## Incorrect assumption caught

An initial idea was to define the active/10-minute rule again in the endpoint or UI. Repository inspection found `backend/services/risk.py` already owns this business rule, and architecture explicitly requires callers to reuse it. The service delegates eligibility to `is_at_risk` instead.

## Decision redirected

The tempting shortcut was to leave the existing click-to-`alert()` behavior and link operators to a URL. I redirected the implementation to fetch the existing detail endpoint and display an inline panel, including an understandable 404 state. Queue buttons use `.at-risk-card`, separate from any general `.order-card` behavior.

## Diff reviewed

Reviewed the implementation diff after the changes: the order list route and payload are untouched; at-risk filtering delegates to the centralized predicate; detail values use `textContent`; and no new fields or frontend dependencies were introduced.

## Tests

`py -m pytest -q` — 9 passed. The API tests cover threshold inclusion, exclusion of below-threshold/null/non-active records through returned behavior, descending delay order, the unchanged existing list, and existing unknown-order 404 behavior.
