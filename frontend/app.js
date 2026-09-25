// DOM Elements
const loadingStateEl = document.getElementById("loading-state");
const errorStateEl = document.getElementById("error-state");
const errorMessageEl = document.getElementById("error-message");
const emptyStateEl = document.getElementById("empty-state");
const tableContainerEl = document.getElementById("table-container");
const ordersTbodyEl = document.getElementById("orders-tbody");
const riskCountEl = document.getElementById("risk-count");
const refreshBtn = document.getElementById("refresh-btn");
const retryBtn = document.getElementById("retry-btn");

// Drawer Elements
const drawerBackdrop = document.getElementById("drawer-backdrop");
const orderDrawer = document.getElementById("order-drawer");
const drawerCloseBtn = document.getElementById("drawer-close-btn");
const drawerTitle = document.getElementById("drawer-title");
const drawerBody = document.getElementById("drawer-body");

/**
 * Format helper for restaurant status pill classes
 */
function getRestaurantPillClass(status) {
  switch (status?.toUpperCase()) {
    case "READY":
      return "pill-ready";
    case "PREPARING":
      return "pill-prep";
    default:
      return "pill-prep";
  }
}

/**
 * Render single order row matching the 5 required columns
 */
function renderOrderRow(order) {
  const delay = order.estimated_delay_minutes;
  const delayBadgeClass = delay >= 15 ? "delay-high" : "delay-medium";
  const restaurantPillClass = getRestaurantPillClass(order.restaurant_status);
  
  const currentEtaDisplay = order.current_eta || "Unknown";
  const supportTag = order.support_opened
    ? `<span class="support-tag support-open">Support Open</span>`
    : `<span class="support-tag support-none">No Ticket</span>`;

  return `
    <tr class="order-row" data-order-id="${escapeHtml(order.order_id)}">
      <!-- Col 1: Order ID -->
      <td class="order-id-cell">
        <span>${escapeHtml(order.order_id)}</span>
      </td>

      <!-- Col 2: Promised / Projected ETA -->
      <td>
        <div class="eta-cell">
          <span class="eta-promised">${escapeHtml(order.promised_eta)}</span>
          <span class="eta-arrow">→</span>
          <span class="eta-current">${escapeHtml(currentEtaDisplay)}</span>
        </div>
      </td>

      <!-- Col 3: Estimated Delay -->
      <td>
        <span class="delay-badge ${delayBadgeClass}">
          +${escapeHtml(String(delay))} min
        </span>
      </td>

      <!-- Col 4: Fulfillment Status -->
      <td>
        <div class="fulfillment-cell">
          <div class="status-row">
            <span class="status-label">Restaurant:</span>
            <span class="status-pill ${restaurantPillClass}">${escapeHtml(order.restaurant_status)}</span>
          </div>
          <div class="status-row">
            <span class="status-label">Driver:</span>
            <span class="status-pill pill-driver">${escapeHtml(order.driver_status)}</span>
          </div>
        </div>
      </td>

      <!-- Col 5: Action / Support -->
      <td>
        <div class="action-cell">
          ${supportTag}
          <button class="btn btn-inspect" data-order-id="${escapeHtml(order.order_id)}">
            Inspect
          </button>
        </div>
      </td>
    </tr>
  `;
}

/**
 * Helper to escape HTML characters
 */
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Fetch at-risk orders and render the dashboard table
 */
async function loadAtRiskOrders() {
  // Set UI state to loading
  loadingStateEl.classList.remove("hidden");
  errorStateEl.classList.add("hidden");
  emptyStateEl.classList.add("hidden");
  tableContainerEl.classList.add("hidden");

  try {
    const response = await fetch("/api/orders/at-risk");
    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status} (${response.statusText})`);
    }

    const atRiskOrders = await response.json();
    loadingStateEl.classList.add("hidden");

    riskCountEl.textContent = atRiskOrders.length;

    if (atRiskOrders.length === 0) {
      emptyStateEl.classList.remove("hidden");
      return;
    }

    // Render rows
    ordersTbodyEl.innerHTML = atRiskOrders.map(renderOrderRow).join("");
    tableContainerEl.classList.remove("hidden");

    // Attach row click listeners for inspection
    document.querySelectorAll(".order-row").forEach((row) => {
      row.addEventListener("click", (e) => {
        const orderId = row.dataset.orderId;
        openOrderDetail(orderId);
      });
    });

  } catch (error) {
    console.error("Failed to load at-risk orders:", error);
    loadingStateEl.classList.add("hidden");
    errorMessageEl.textContent = error.message;
    errorStateEl.classList.remove("hidden");
    riskCountEl.textContent = "!";
  }
}

/**
 * Fetch complete order details and open slide-over inspection drawer
 */
async function openOrderDetail(orderId) {
  drawerTitle.textContent = `Order ${orderId}`;
  drawerBody.innerHTML = `
    <div class="state-container">
      <div class="spinner"></div>
      <p>Loading details for ${escapeHtml(orderId)}…</p>
    </div>
  `;

  // Show drawer
  drawerBackdrop.classList.remove("hidden");
  orderDrawer.classList.remove("hidden");
  document.body.style.overflow = "hidden";

  try {
    const response = await fetch(`/api/orders/${encodeURIComponent(orderId)}`);
    if (!response.ok) {
      throw new Error(`Could not fetch order details (HTTP ${response.status})`);
    }

    const order = await response.json();
    renderDrawerDetails(order);

  } catch (error) {
    drawerBody.innerHTML = `
      <div class="error-banner">
        <div class="error-icon">⚠️</div>
        <div class="error-text">
          <strong>Failed to load order</strong>
          <p>${escapeHtml(error.message)}</p>
        </div>
      </div>
    `;
  }
}

/**
 * Render drawer detail view sections
 */
function renderDrawerDetails(order) {
  const delayBadgeClass = order.estimated_delay_minutes >= 15 ? "delay-high" : "delay-medium";
  const restaurantPillClass = getRestaurantPillClass(order.restaurant_status);
  const supportTag = order.support_opened
    ? `<span class="support-tag support-open">Active Ticket Open</span>`
    : `<span class="support-tag support-none">No Ticket Opened</span>`;

  drawerBody.innerHTML = `
    <!-- Section 1: Timing & Delay -->
    <div class="drawer-section">
      <h3 class="section-title">Timing & Delay Analysis</h3>
      <div class="detail-grid">
        <div class="detail-item">
          <span class="detail-label">Promised ETA</span>
          <span class="detail-value">${escapeHtml(order.promised_eta)}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Projected ETA</span>
          <span class="detail-value">${escapeHtml(order.current_eta || "Unknown")}</span>
        </div>
        <div class="detail-item full-width">
          <span class="detail-label">Estimated Delay</span>
          <div>
            <span class="delay-badge ${delayBadgeClass}">+${escapeHtml(String(order.estimated_delay_minutes))} minutes</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Section 2: Fulfillment Status -->
    <div class="drawer-section">
      <h3 class="section-title">Fulfillment Progress</h3>
      <div class="detail-grid">
        <div class="detail-item">
          <span class="detail-label">Order Lifecycle</span>
          <span class="detail-value">${escapeHtml(order.status)}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Kitchen Status</span>
          <div>
            <span class="status-pill ${restaurantPillClass}">${escapeHtml(order.restaurant_status)}</span>
          </div>
        </div>
        <div class="detail-item full-width">
          <span class="detail-label">Courier Status</span>
          <div>
            <span class="status-pill pill-driver">${escapeHtml(order.driver_status)}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Section 3: Support & Interventions -->
    <div class="drawer-section">
      <h3 class="section-title">Support History & Previous Interventions</h3>
      <div class="detail-grid">
        <div class="detail-item">
          <span class="detail-label">Customer Support</span>
          <div>${supportTag}</div>
        </div>
        <div class="detail-item">
          <span class="detail-label">Last Intervention</span>
          <span class="detail-value">${escapeHtml(order.previous_intervention || "None recorded")}</span>
        </div>
      </div>
    </div>

    <!-- Section 4: Proactive Guidance -->
    <div class="drawer-section">
      <div class="guidance-box">
        <h4>Proactive Support Recommendation</h4>
        <p>${getRecommendation(order)}</p>
      </div>
    </div>
  `;
}

/**
 * Generate contextual operational recommendation
 */
function getRecommendation(order) {
  if (order.restaurant_status === "READY" && order.driver_status.includes("away")) {
    return `Food is ready at restaurant. Courier is ${escapeHtml(order.driver_status)}. Send automated ETA update message to customer if not already sent.`;
  }
  if (order.restaurant_status === "PREPARING" && order.estimated_delay_minutes >= 10) {
    return `Kitchen preparation is running behind schedule. Contact restaurant or notify customer of revised ETA window.`;
  }
  if (order.support_opened) {
    return `Customer has an open support inquiry. Coordinate directly with support agent handling the ticket.`;
  }
  return `Review current order state and monitor courier transit.`;
}

/**
 * Close drawer and reset backdrop
 */
function closeDrawer() {
  drawerBackdrop.classList.add("hidden");
  orderDrawer.classList.add("hidden");
  document.body.style.overflow = "";
}

// Event Listeners
refreshBtn.addEventListener("click", loadAtRiskOrders);
retryBtn.addEventListener("click", loadAtRiskOrders);
drawerCloseBtn.addEventListener("click", closeDrawer);
drawerBackdrop.addEventListener("click", closeDrawer);

// Close on Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !orderDrawer.classList.contains("hidden")) {
    closeDrawer();
  }
});

// Initial load
loadAtRiskOrders();

