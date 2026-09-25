const ordersEl = document.getElementById("orders");
const messageEl = document.getElementById("message");

function orderCard(order) {
  const delay = order.estimated_delay_minutes;
  const delayText = delay === null ? "Unknown delay" : `${delay} min`;

  return `
    <button class="order-card" data-order-id="${order.order_id}">
      <div>
        <strong>${order.order_id}</strong>
        <span>${order.status}</span>
      </div>
      <div>
        <span>Promised ${order.promised_eta}</span>
        <span>${delayText}</span>
      </div>
    </button>
  `;
}

async function loadOrders() {
  try {
    const response = await fetch("/api/orders");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const orders = await response.json();
    messageEl.textContent = `${orders.length} orders loaded`;
    ordersEl.innerHTML = orders.map(orderCard).join("");

    document.querySelectorAll(".order-card").forEach((button) => {
      button.addEventListener("click", () => {
        const orderId = button.dataset.orderId;
        window.alert(`Order detail is available at /api/orders/${orderId}`);
      });
    });
  } catch (error) {
    messageEl.textContent = `Could not load orders: ${error.message}`;
  }
}

const queueEl = document.getElementById("queue");
const queueMessageEl = document.getElementById("queue-message");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function queueCard(order) {
  const currentEta = order.current_eta ?? "Unknown";
  const support = order.support_opened ? "Support ticket open" : "No support ticket";
  const intervention = order.previous_intervention ?? "None";

  return `
    <button class="order-card queue-card" data-order-id="${escapeHtml(order.order_id)}">
      <div>
        <strong>${escapeHtml(order.order_id)}</strong>
        <span class="delay">${escapeHtml(order.estimated_delay_minutes)} min late</span>
      </div>
      <div>
        <span>Promised ${escapeHtml(order.promised_eta)}</span>
        <span>Now ${escapeHtml(currentEta)}</span>
      </div>
      <div>
        <span>Restaurant: ${escapeHtml(order.restaurant_status)}</span>
        <span>Driver: ${escapeHtml(order.driver_status)}</span>
      </div>
      <div>
        <span>${support}</span>
        <span>Previous intervention: ${escapeHtml(intervention)}</span>
      </div>
    </button>
  `;
}

async function loadQueue() {
  try {
    const response = await fetch("/api/at-risk-orders");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const orders = await response.json();
    if (orders.length === 0) {
      queueMessageEl.textContent = "No active orders are delayed 10+ minutes right now.";
      queueEl.innerHTML = "";
      return;
    }

    const noun = orders.length === 1 ? "order" : "orders";
    queueMessageEl.textContent = `${orders.length} active ${noun} delayed 10+ minutes, most delayed first`;
    queueEl.innerHTML = orders.map(queueCard).join("");
  } catch (error) {
    queueMessageEl.classList.add("error");
    queueMessageEl.textContent = `Could not load at-risk orders: ${error.message}`;
  }
}

loadQueue();
loadOrders();
