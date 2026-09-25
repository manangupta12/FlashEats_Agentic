const atRiskOrdersEl = document.getElementById("at-risk-orders");
const atRiskMessageEl = document.getElementById("at-risk-message");
const atRiskBadgeEl = document.getElementById("at-risk-badge");

const ordersEl = document.getElementById("orders");
const messageEl = document.getElementById("message");

function orderCard(order, isRiskView = false) {
  const delay = order.estimated_delay_minutes;
  const delayText = delay === null ? "Unknown delay" : `+${delay} min delay`;
  const supportTag = order.support_opened ? `<span class="tag tag-support">Support Ticket</span>` : "";
  const extraInfo = isRiskView
    ? `<div class="card-details">
        <span>Restaurant: <strong>${order.restaurant_status}</strong></span>
        <span>Driver: <strong>${order.driver_status}</strong></span>
        ${supportTag}
       </div>`
    : "";

  return `
    <button class="order-card ${isRiskView ? "at-risk-card" : ""}" data-order-id="${order.order_id}">
      <div class="card-main">
        <div>
          <strong>${order.order_id}</strong>
          <span class="status-tag">${order.status}</span>
        </div>
        <div>
          <span>Promised ${order.promised_eta}</span>
          <span class="delay-tag ${isRiskView ? "delay-high" : ""}">${delayText}</span>
        </div>
      </div>
      ${extraInfo}
    </button>
  `;
}

function attachCardClickListeners() {
  document.querySelectorAll(".order-card").forEach((button) => {
    button.addEventListener("click", () => {
      const orderId = button.dataset.orderId;
      window.alert(`Order detail is available at /api/orders/${orderId}`);
    });
  });
}

async function loadAtRiskOrders() {
  try {
    const response = await fetch("/api/orders/at-risk");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const atRiskOrders = await response.json();
    atRiskBadgeEl.textContent = atRiskOrders.length;

    if (atRiskOrders.length === 0) {
      atRiskMessageEl.textContent = "No active orders currently at risk. All live deliveries are operating within normal parameters.";
      atRiskOrdersEl.innerHTML = "";
    } else {
      atRiskMessageEl.textContent = `${atRiskOrders.length} order(s) requiring immediate attention`;
      atRiskOrdersEl.innerHTML = atRiskOrders.map((o) => orderCard(o, true)).join("");
    }
  } catch (error) {
    atRiskMessageEl.textContent = `Could not load at-risk queue: ${error.message}`;
  }
}

async function loadOrders() {
  try {
    const response = await fetch("/api/orders");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const orders = await response.json();
    messageEl.textContent = `${orders.length} total orders listed`;
    ordersEl.innerHTML = orders.map((o) => orderCard(o, false)).join("");
  } catch (error) {
    messageEl.textContent = `Could not load orders: ${error.message}`;
  }
}

async function init() {
  await Promise.all([loadAtRiskOrders(), loadOrders()]);
  attachCardClickListeners();
}

init();

