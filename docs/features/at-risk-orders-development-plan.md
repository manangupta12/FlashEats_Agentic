### 1. Current State

#### Existing
- The repository is a small internal operations dashboard for FlashEats.
- The app currently serves a browser UI and exposes a minimal Flask API.
- Existing routes are defined in `backend/api.py` and provide:
  - `GET /` for the dashboard shell
  - `GET /api/orders` to list all orders
  - `GET /api/orders/<order_id>` to fetch a single order
- Order data is read from the static JSON dataset in `backend/data/orders.json` via `backend/services/orders.py`.
- The core business rule is already centralized in `backend/services/risk.py` as `is_at_risk(order)`: an order is treated as at risk only when it is `ACTIVE`, the delay value is known, and the delay is at least 10 minutes.
- The current tests in `tests/test_orders_api.py` and `tests/test_risk.py` confirm these behaviors and the current API contract.
- The frontend in `frontend/app.js` loads the order list and renders basic order cards.

#### Missing for the functional spec
- There is no dedicated at-risk queue or prioritization view.
- There is no visible distinction between delayed orders and other active orders beyond the raw list.
- There is no prioritization logic that considers both delay and support tickets.
- There is no empty-state experience for the scenario where no orders are at risk.
- There is no explicit handling for negative delay values beyond the business rule interpretation; current data quality handling is not yet surfaced as a user-facing workflow.
- There is no support-ticket-aware prioritization in the product flow.

#### Existing vs. required
- Existing: active order + delay threshold rule
- Required: queue/prioritization plus support-ticket influence
- Existing: internal dashboard nature
- Required: operational triage view focused on intervention priority

### 2. Implementation Plan

#### Task 1: Confirm the product-facing definition of the at-risk queue
**Task**
- Define the MVP behavior for the at-risk order list in product terms without changing system architecture.
- Align the implementation around the confirmed functional rules and leave unresolved business decisions explicit.

**Why**
- This satisfies the functional requirement that the at-risk view identifies orders requiring intervention.
- It also ensures the team is working from a clear product definition before changing code.

**Likely Files/Areas**
- `docs/features/at-risk-orders-functional-spec.md`
- Existing business rule logic in `backend/services/risk.py`
- Any future feature documentation or backlog tickets related to this feature

**Expected Behavior**
- The team has a shared understanding that the at-risk focus is on active, delayed orders, with customer support status affecting priority.
- Known open questions are explicitly tracked rather than silently decided.

**Validation**
- Product/engineering review of the functional spec
- Acceptance criteria review against the current repo behavior and product goals

---

#### Task 2: Establish the at-risk filtering contract in the existing service layer
**Task**
- Update the business logic so the system can identify which orders belong in the at-risk view.
- Reuse the existing risk rule and extend it to the MVP queue definition without changing the broader order model.

**Why**
- This satisfies the requirement that only qualifying orders appear in the at-risk view.
- It supports missing delay handling and negative delay handling as data-quality exceptions.

**Likely Files/Areas**
- `backend/services/risk.py`
- `tests/test_risk.py`
- Potentially `backend/models.py` if field semantics need to be clarified for the current business rule

**Expected Behavior**
- Orders are only considered at risk when they meet the rule for eligible active orders.
- Missing delay = not risky.
- Negative delay = excluded as invalid for risk classification.
- Completed and cancelled orders remain excluded.

**Validation**
- Unit tests for eligible vs. ineligible orders
- Regression checks on existing risk tests
- Manual review of data-edge cases from `backend/data/orders.json`

---

#### Task 3: Define and document the prioritization rules for the queue
**Task**
- Establish the ordering principle for the at-risk view using delay first and support ticket presence as a tie-breaker or higher-priority signal.
- Keep this at the product behavior level and avoid hard-coding unsupported business decisions.

**Why**
- This satisfies the requirement to prioritize delayed orders and orders with customer support tickets.
- It resolves the core experience gap for the at-risk queue.

**Likely Files/Areas**
- `docs/features/at-risk-orders-functional-spec.md`
- `backend/services/risk.py` or a narrow order-view helper if needed
- `tests/test_risk.py` or new queue-focused tests

**Expected Behavior**
- The queue presents the highest-priority orders first, based on the agreed order of significance.
- The team can explain why one order ranks ahead of another.

**Validation**
- Scenario-based tests covering multiple delayed orders and support-ticket variants
- Review with Ops stakeholders for priority rationale

---

#### Task 4: Add the at-risk view behavior to the backend contract
**Task**
- Expose the at-risk result through the existing API layer in a way that does not break current order endpoints.
- Preserve current list/detail behavior while adding the queue-specific behavior in a backwards-compatible way.

**Why**
- This satisfies the user-facing requirement that Ops can see the at-risk queue.
- It keeps existing contract stability while introducing the new business view.

**Likely Files/Areas**
- `backend/api.py`
- `backend/services/orders.py`
- Existing API tests in `tests/test_orders_api.py`

**Expected Behavior**
- Current endpoints continue to work as before.
- The at-risk view is available via the intended product contract without breaking existing consumers.
- The result is clearly scoped to the eligible, prioritized set of orders.

**Validation**
- Existing API tests still pass
- New tests confirm route behavior for the at-risk subset view
- Contract review to ensure no accidental breaking change to `/api/orders`

---

#### Task 5: Update the current UI to render the at-risk queue and empty state
**Task**
- Adapt the existing frontend experience to display the at-risk queue instead of or alongside the current order list.
- Ensure the view is useful for Ops with enough context to triage an order and a clear empty state.

**Why**
- This satisfies the functional requirement that Ops see the orders needing attention and understand what they are looking at.
- It addresses the requirement for a useful empty-state experience when there are no at-risk orders.

**Likely Files/Areas**
- `frontend/index.html`
- `frontend/app.js`
- `frontend/styles.css` if needed for lightweight presentation changes

**Expected Behavior**
- At-risk orders are shown in order of urgency.
- Ops can tell which orders are delayed and whether support has been opened.
- When no at-risk orders exist, the user sees an explicit empty message.

**Validation**
- Manual browser verification against a known sample dataset
- QA review of order display and empty-state behavior
- Regression check that regular order listing still functions if kept in place

---

#### Task 6: Populate test data and validate data quality handling in the feature context
**Task**
- Validate the existing sample order set so the feature is exercised against realistic states including active, delayed, missing delay, cancelled, and support-ticket cases.
- Confirm that negative delay values are treated as invalid and excluded from risk ranking.

**Why**
- This satisfies the requirement to handle data-quality edge cases and keeps the feature safe in real operations.

**Likely Files/Areas**
- `backend/data/orders.json`
- `tests/test_risk.py`
- `tests/test_orders_api.py`

**Expected Behavior**
- Sample data covers the business edge cases relevant to the MVP.
- Negative delays do not cause false at-risk classification.
- Support-ticket orders are visible in the prioritization logic when present.

**Validation**
- Explicit test cases for missing delay, negative delay, and support-ticket ordering
- Data review to confirm the sample data reflects intended product behavior

---

#### Task 7: Final regression and business acceptance pass
**Task**
- Run the minimal regression suite and review the product behavior against the acceptance criteria.
- Confirm the feature is effectively MVP-ready and does not widen scope beyond the approved requirements.

**Why**
- This ensures the feature meets the functional spec without breaking existing functionality.

**Likely Files/Areas**
- `tests/*`
- feature doc review and product signoff

**Expected Behavior**
- Existing behavior still works.
- New at-risk behavior is observable and matches expected priority rules.
- Open questions are explicitly tracked rather than accidentally assumed.

**Validation**
- Local test run
- Business validation of queue behavior
- Review of empty-state, prioritization, and data-edge cases

### 3. Business Logic Changes

#### Existing business rules that can be reused
- Active orders are the relevant operational class for intervention.
- Delay is a primary signal for risk.
- Delay threshold is at least 10 minutes.
- Missing delay is not treated as risk.
- Completed and cancelled orders are excluded from intervention.
- Support ticket status is relevant to prioritization.

#### Rules that need to change
- The system currently exposes the raw order list; it does not yet expose a queue or prioritized list.
- The operational risk concept needs to become a product-facing at-risk view rather than only a service-level helper.
- Prioritization needs to combine delay severity and support ticket presence.

#### New rules that need to be introduced
- Orders with a support ticket should be prioritized ahead of otherwise similar delayed orders.
- A dedicated at-risk view should surface only eligible orders.
- Negative delays should be treated as invalid for risk classification and excluded from prioritization.
- An empty state must be surfaced when no orders qualify.

#### Edge cases that must be handled
- Missing delay value
- Negative delay value
- Active order below threshold
- Completed or cancelled order with historically high delay
- Multiple orders with similar delays but different support status
- No orders currently at risk

#### Unknown / needs confirmation
- Exact ordering of multiple delayed orders when delay values and support status are mixed
- Whether support tickets should always outrank delay, or only when delay is within a certain range
- Whether there are any additional exclusions for active orders not requiring intervention
- What minimal order details are necessary for Ops to triage effectively

### 4. Data Changes

#### Existing
- Order structure already exists in `backend/data/orders.json` and the `Order` TypedDict in `backend/models.py`.
- The current fields appear sufficient for the MVP requirements.

#### Change required
- No new core data model is required for the initial feature, assuming the existing fields already include the relevant operational details.
- The feature may require using existing fields in a different way rather than adding new persistence fields.

#### New
- No new order lifecycle state is required in the MVP unless product decisions require a new explicit queue state.
- No new data schema is required at the current scope.

#### Unknown / needs confirmation
- Whether `support_opened` alone is sufficient for prioritization or whether additional ticket metadata is required later
- Whether the current dataset should include additional summary fields for triage in the UI

#### Data-model conclusion
- For the current MVP, no data-model change is required. The business logic can be implemented using the existing order records and current fields.

### 5. API / Interface Changes

#### Existing interfaces
- `GET /api/orders` continues to return the full order list.
- `GET /api/orders/<order_id>` continues to return a single order.
- These routes must remain stable for existing consumers unless product scope explicitly changes them.

#### Change required
- Introduce a queue-specific view or a filtered ordering contract for the at-risk subset.
- Keep the feature incremental and avoid breaking the existing list/detail behavior.

#### New interfaces
- A new at-risk order view may be required if the product needs a distinct prioritized queue rather than a filtered list embedded into existing routes.
- The interface contract should remain at the behavior level: “return only qualifying, prioritized orders” without dictating implementation details.

#### Unknown / needs confirmation
- Whether the at-risk view is a separate route, a filter on the existing list, or part of the same dashboard contract
- Whether the product expects new API fields for queue metadata beyond the existing order records

### 6. UI / User Workflow Changes

#### Existing workflow
- The user loads the dashboard and sees the current list of orders.
- The current UI renders cards with basic order information and delay text.

#### Change required
- The experience should prioritize orders needing intervention, with a clear at-risk queue for Ops.
- The user should be able to identify delayed orders quickly and see whether a support ticket was opened.
- The user should see a useful empty state when no at-risk orders exist.

#### User-visible behavior
- Ops sees a focused list of at-risk orders, ordered by urgency.
- The list highlights or prioritizes orders with both delay and support ticket activity.
- Delay values are shown in a recognizable way, and missing/invalid values are handled appropriately.
- When no at-risk orders exist, the view communicates that clearly.

#### Unknown / needs confirmation
- The exact visual treatment for priority ranking and support-ticket presence
- Whether the at-risk queue replaces the raw list or sits alongside it

### 7. Testing Plan

#### Existing behavior that must not break
- `GET /api/orders` still returns all orders
- `GET /api/orders/<order_id>` still returns the expected order or a 404
- Existing risk rule semantics remain valid for active orders and delay threshold logic

#### New happy paths
- An active delayed order qualifies for the at-risk list
- A delayed order with a support ticket ranks above a delayed order without a support ticket
- A threshold-equality order (delay = 10) qualifies
- A non-risk order is absent from the queue

#### Edge cases
- delay = `null` => not at risk
- delay < 0 => excluded as invalid
- status = `DELIVERED` or `CANCELLED` => excluded
- delay = 9 => excluded
- no orders qualify => empty state

#### Invalid / missing data
- Unknown delay values should not produce false positives
- Negative delay values should not be treated as a valid risk signal
- Missing support status should not create a false confidence signal

#### Prioritization behavior
- Highest delay first
- Support-ticket orders rise above otherwise similar delayed orders
- Priority behavior remains stable and explainable for QA and Ops review

#### Mapping to acceptance criteria
- At-risk qualification: covered by status, delay, negative delay, and missing-delay tests
- Inactive order exclusion: covered by completed and cancelled order tests
- Support ticket influence: covered by prioritization test cases
- Empty-state behavior: covered by no-qualifying-order tests

### 8. Rollout / Verification

#### Local verification
- Run the existing test suite with the repo’s current import pattern: `PYTHONPATH=. pytest -q`
- Confirm the queue feature does not break current order API behavior
- Verify the at-risk view with sample data that includes all edge cases from the functional spec

#### Regression checks
- Existing order API tests remain green
- Existing risk rule tests remain green
- The frontend still loads successfully and does not fail when no at-risk orders are present

#### Business acceptance checks
- Review the prioritized queue with Ops to confirm the ranking makes operational sense
- Confirm that support tickets materially influence prioritization
- Confirm that inactive or cancelled orders are not shown in intervention context

#### Data-quality checks
- Check for null and negative delay values in sample and test data
- Confirm the product treats invalid delay values as non-risk rather than as actual delay severity
- Confirm the support ticket field is used consistently in the view and ranking logic

### 9. Dependencies & Risks

#### Technical dependencies
- The repository is a lightweight Flask app with static JSON data; this makes the feature easy to implement without introducing new architecture.
- The feature will likely depend on the existing order dataset and business rule logic.
- The current implementation is intentionally minimal; therefore the main technical risk is preserving the existing contracts while adding the queue view.

#### Business dependencies
- The actual priority rule between delay and support tickets still needs product confirmation.
- The team needs to confirm whether the at-risk view replaces the full order list or supplements it.
- The required display fields for actionable triage need business validation.

#### Data dependencies
- The current data source is static and limited; feature behavior depends on the quality of data in `backend/data/orders.json`.
- Negative and missing delay values must be treated intentionally and consistently.

#### Ambiguities that could block implementation
- Exact priority ordering across support and delay signals
- Whether support tickets should be treated as a strict override or as a secondary signal
- Whether certain active orders should be excluded for business reasons beyond the current rules

#### Regression risks
- Breaking the current `/api/orders` contract by filtering unexpectedly
- Incorrectly excluding valid active orders because of overly strict delay handling
- Showing stale or misleading delay values in the at-risk view
- Expanding the feature scope beyond the MVP and introducing non-essential complexity

### 10. Definition of Done

- The at-risk view reflects the confirmed functional criteria for active, delayed orders.
- Inactive, cancelled, and completed orders are excluded from active intervention.
- Missing delay values are not treated as risk.
- Negative delays are treated as invalid and excluded from risk classification.
- Customer support tickets influence prioritization as required by the functional spec.
- Delayed orders are prioritized appropriately.
- The empty state is clear and user-friendly when no orders qualify.
- Existing order API and risk logic remain stable and regression-tested.
- The feature is documented and traceable back to the acceptance criteria.
- Open business questions are explicitly identified and not silently assumed.
- The feature is limited to the approved MVP scope and does not introduce unsupported operational or customer-facing functionality.
