# Functional Spec — At-Risk Orders Queue

**Status:** Authoritative product spec for this feature.  
**Supersedes for requirements:** [at-risk-orders-starter.md](at-risk-orders-starter.md) (starter request kept for history).

## Summary

FlashEats Operations needs a focused queue of active orders that meet the existing at-risk business rule, ordered by urgency, so an Operations Manager can decide which order to inspect next during busy service.

## User

Operations Manager (internal ops console user).

## Goal

Quickly identify active orders that require review now, without scanning the full order list.

## Business rule

An order is **at risk** only when the existing centralized rule says so:

- status is `ACTIVE`, and
- `estimated_delay_minutes` is known (not null), and
- `estimated_delay_minutes` is at least 10.

Product language such as *late*, *delayed*, or *at risk* must not introduce a second classification rule. Unknown delay must never be treated as a numeric risk.

Completed (`DELIVERED`) and cancelled (`CANCELLED`) orders must not appear in the queue, even if they have large delay values.

## Most urgent

Among at-risk orders, higher `estimated_delay_minutes` means more urgent. The queue must list orders with higher delay first.

## User flows

### Happy path

1. Operations Manager opens the FlashEats Operations console.
2. They see an **At-Risk Orders** queue of actionable at-risk orders only.
3. Orders appear with the most urgent (highest delay) first.
4. Each row shows enough information to choose the next order to inspect: order id, status, promised ETA, and delay.
5. Selecting an order reuses the existing order-detail capability (existing detail API / current detail interaction).

### Empty queue

1. When no orders meet the at-risk rule, the queue shows a useful empty state.
2. The empty state makes clear that no active orders currently need review via this queue.

## UI requirements

- Dedicated At-Risk Orders queue section (not only the existing all-orders list).
- Queue rows display: `order_id`, `status`, promised ETA, and delay text.
- Selecting a queue row uses the same order-detail behavior already available in the app (no new detail product).
- Empty state when the queue has zero items.

## Acceptance criteria

1. Only orders matching the existing at-risk rule appear in the queue.
2. Orders with status `DELIVERED` or `CANCELLED` never appear.
3. Orders with unknown (`null`) delay never appear.
4. Active orders with delay below 10 minutes never appear.
5. Queue ordering is by `estimated_delay_minutes` descending.
6. With current seed data, queue order is: FE-48291 (18), FE-48293 (14), FE-48297 (10).
7. Selecting an order reuses the existing order-detail capability.
8. When no at-risk orders exist, a clear empty state is shown.
9. Existing all-orders list and order-detail API contracts remain stable.
10. MVP does not add driver reassignment, refunds, maps, or predictive-model features.

## Out of scope

- Driver reassignment
- Refunds or compensation workflows
- Maps or live location tracking
- Predictive models or new risk scoring fields
- Redesigning the full order-detail experience beyond reusing what exists
- Database, queues, or new application frameworks

## Constraints

- Do not invent order fields that are not already in the order model / data.
- Do not silently convert unknown delay into a numeric risk value.
- Existing API contracts for listing all orders and fetching one order remain stable unless a requirement explicitly changes them.
