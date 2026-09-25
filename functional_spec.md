## User

FlashEats Operations Team

## Goal

A way to surface delayed/risky orders so that the operations team can focus where intervention may be needed.

## Acceptance criteria

* The system must display a dedicated queue of active orders that meet the "at-risk" criteria.
* The queue must automatically sort orders by urgency, ensuring the most critical orders appear at the top.
* Each item in the queue must display high-level summary information (using only existing fields) to help the user decide which order to investigate first.
* Selecting an order from the queue must navigate the user directly to the existing Order Detail view.
* The queue must display a clear and useful empty state when there are no at-risk orders.

## Out of scope

* Driver reassignment workflows.
* Refund processing and payment adjustments.
* Map integrations or spatial tracking features.
* Predictive models or machine learning algorithms to calculate order risk.

## Open questions

* What existing backend flags or business rules currently define an active order as "risky" or "delayed"?
* What existing data points dictate the logic for sorting by urgency (e.g., minutes past ETA, order value)?
* Which specific fields are currently available in the API to populate the order summary card without requiring backend additions?