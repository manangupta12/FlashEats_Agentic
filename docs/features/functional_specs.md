# Functional Specification: At-Risk Orders Queue

## 1. User
Operations Manager

## 2. Goal
Quickly identify active orders that require review and intervention during a busy service period.

## 3. Acceptance criteria
- The queue displays only active orders that are classified as "at risk".
- An order is "at risk" if its estimated delay is exactly 10 minutes or greater (utilizing the existing service rule).
- Orders with an unknown delay are excluded from the queue.
- Non-active orders (e.g., delivered or cancelled) are excluded from the queue.
- The queue must be sorted so the most urgent orders (highest estimated delay) appear first.
- Each item in the queue shows enough information (e.g., order ID, delay, status) to decide what to inspect.
- Selecting an order from the queue reuses the existing order-detail capability.
- A clear empty state is displayed when there are no at-risk orders.

## 4. Out of scope
- Driver reassignment in the MVP.
- Automated refunds.
- Map integrations.
- Predictive model work for ETAs.

## 5. Open questions
- Should "urgent" sorting strictly use descending `estimated_delay_minutes`, or should `promised_eta` also be considered as a tie-breaker?
- What exact fields should be displayed on the queue list besides `order_id` and `estimated_delay_minutes`?
