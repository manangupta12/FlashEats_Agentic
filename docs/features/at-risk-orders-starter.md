# Feature Request — At-Risk Orders Queue

> Refined specs (source of truth): [at-risk-orders-functional-spec.md](at-risk-orders-functional-spec.md), [at-risk-orders-technical-spec.md](at-risk-orders-technical-spec.md).

The Operations team wants a small queue that helps them identify orders that need attention during a busy service period.

## User
Operations Manager

## Goal
Quickly identify active orders that require review.

## Requested experience

- Show risky active orders.
- Put the most urgent orders first.
- Show enough information to decide which order to inspect next.
- Selecting an order should reuse the existing order-detail capability.
- Provide a useful empty state.
- Do not expand the MVP into driver reassignment, refunds, maps, or predictive-model work.

## Before implementation

Clarify anything in this request that is not sufficiently precise by inspecting the repository and existing business rules.

Do not invent missing fields or APIs.
