# 1. User

The primary user is an Operations Manager who uses FlashEats’ internal Operations dashboard to monitor live delivery activity during busy periods. This user is responsible for identifying orders that need attention and deciding where intervention may be needed. They are already engaged in customer support operations, so they need to understand both delivery delay and whether the customer has raised a support ticket for an order.

This user is familiar with operational order states and service disruptions but does not need a detailed technical view of the system. Their goal is to quickly assess which active orders require attention and to triage the most urgent items first.

# 2. Goal

FlashEats needs a simple way for Ops to identify active orders that require attention, especially when an order is delayed or a customer has already raised a support issue. The desired outcome is to help the Operations team focus on the orders that are most likely to need intervention, without broadening the scope into other operational workflows or customer-facing experiences.

# 3. Acceptance Criteria

- Given an order that is ACTIVE, has a known delay, and the delay is at least 10 minutes, When the Ops at-risk view is generated, Then the order qualifies for the at-risk view.

- Given an order that is not ACTIVE, such as completed or cancelled, When the at-risk view is generated, Then the order is not shown as requiring active intervention.

- Given an order whose delay is missing or unknown, When the at-risk view is generated, Then the order is not treated as at risk based on delay alone.

- Given an order whose delay is a negative value, When the at-risk view is generated, Then the negative value is treated as a data-quality issue and is not used to classify the order as at risk.

- Given an order with a customer support ticket raised, When the at-risk view is sorted or prioritized, Then that order is treated as higher priority than comparable orders without an active support ticket.

- Given multiple orders that qualify as at risk, When the at-risk view is presented, Then the most delayed orders appear first, with orders that also have customer support tickets ranked ahead of similar delayed orders without support tickets.

- Given an order that is delayed and has a support ticket, When Ops reviews the at-risk view, Then the order should be visible with enough information for triage, including the key operational details needed to understand the issue and decide next action.

- Given an order that is active but not delayed enough to qualify, When the at-risk view is generated, Then it is not included in the at-risk queue.

- Given an order that is active and delayed but already has a support ticket, When Ops reviews the queue, Then the ticket status remains relevant to prioritization even if the delay is not the largest in the list.

- Given there are no orders that qualify for the at-risk view, When the Ops view is opened, Then the user sees a clear empty state indicating there are currently no at-risk orders requiring attention.

- Given an order that has an active status and a known delay of exactly 10 minutes, When the at-risk view is generated, Then the order is included as at risk because the threshold is met.

- Given an order that has an active status and a known delay of 9 minutes, When the at-risk view is generated, Then the order is not included as at risk because it is below the threshold.

- Given an order with a delay and a support ticket, When Ops needs to decide the order’s urgency, Then both delay and support status are considered as prioritization inputs.

# 4. Out of Scope

This feature does not include:
- Customer-facing order tracking or customer notifications
- Driver reassignment or dispatch changes
- Refunds, compensation, or billing actions
- Maps, navigation, or route guidance
- Predictive ML or forecasting models
- Support workflow management, including creating, resolving, or assigning support tickets
- Authentication, authorization, or role-based access changes
- Real external integrations with upstream systems or data providers
- Monitoring, alerting, or operational dashboards beyond the at-risk view
- Changing the underlying order lifecycle or order state model

# 5. Open Questions

- What should the exact priority ordering be when multiple orders are delayed?
  - This matters because the product needs a clear and consistent rule for ordering orders when several delay and support cases are present.

- How should an order with both a significant delay and a support ticket compare with other at-risk orders?
  - This matters because the business needs a precedence rule for when multiple risk signals are present.

- What customer/order information is necessary for Ops to communicate with the customer?
  - This matters because the at-risk queue should show enough information for effective triage, and the required information could affect the display and prioritization.

- Are there business rules for excluding certain active orders from intervention even if they are delayed?
  - This matters because not every active delayed order may require ops action, and such exceptions may affect who qualifies.

- What should happen when order data is incomplete or stale?
  - This matters because data-quality issues can cause uncertainty in risk classification and may require rules for handling incomplete records.
