# Functional Feature Spec: At-Risk Orders Queue

## 1. User
Operations Manager

## 2. Goal
Quickly identify active orders that require review and intervention during a busy service period.

## 3. Acceptance criteria
- The system must display a queue of only "at-risk" active orders.
- An order is defined as "at-risk" using the existing Operations business rule (it must be active, have a known estimated delay, and the delay must be at least 10 minutes).
- The queue must prioritize the most urgent orders first (sorted so that orders with the longest estimated delay appear at the top).
- Each entry in the at-risk queue must display sufficient information for the user to make a quick decision (e.g., Order ID, Status, Promised ETA, and Delay duration).
- Selecting an order from the at-risk queue must provide the exact same order-detail capability (viewing order details) as selecting an order from the standard list.
- If there are no at-risk orders, the queue must display a clear and reassuring empty state indicating that no orders currently require attention.

## 4. Out of scope
- Modifying or redefining the business rules for what constitutes an "at-risk" order.
- Adding new resolution workflows (e.g., driver reassignment, issuing refunds, map views, or predictive-model changes).
- Changing the existing standard order list functionality.

## 5. Open questions
- When prioritizing by urgency, if two orders have the exact same estimated delay, should they be sorted by a secondary metric (such as earliest promised ETA)?
- Should this new at-risk queue completely replace the existing "all orders" view on the main screen, or should they be visible side-by-side to the Operations Manager?
