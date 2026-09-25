const ordersEl = document.getElementById("orders");
const messageEl = document.getElementById("message");
const detailEl = document.getElementById("detail");

function orderCard(order) {
  const delay = order.estimated_delay_minutes;
  const delayText = delay === null ? "Unknown delay" : `${delay} min`;

  return `
    <button class="order-card" data-order-id="${order.order_id}">
      <div>
        <strong>${order.order_id}</strong>
        <span class="status">${order.status}</span>
      </div>
      <div>
        <span>Promised ${order.promised_eta}</span>
        <span>${delayText}</span>
      </div>
    </button>
  `;
}

function renderDetail(order) {
  const delayText = order.estimated_delay_minutes === null
    ? "Unknown delay"
    : `${order.estimated_delay_minutes} min`;
  const currentEta = order.current_eta || "Not available";
  const previousIntervention = order.previous_intervention || "None";

  detailEl.hidden = false;
  detailEl.innerHTML = `
    <div class="detail-heading">
      <div>
        <p class="eyebrow">ORDER DETAIL</p>
        <h2>${order.order_id}</h2>
      </div>
      <button class="close-detail" type="button">Close</button>
    </div>
    <dl class="detail-grid">
      <div><dt>Status</dt><dd>${order.status}</dd></div>
      <div><dt>Delay</dt><dd>${delayText}</dd></div>
      <div><dt>Promised ETA</dt><dd>${order.promised_eta}</dd></div>
      <div><dt>Current ETA</dt><dd>${currentEta}</dd></div>
      <div><dt>Restaurant</dt><dd>${order.restaurant_status}</dd></div>
      <div><dt>Driver</dt><dd>${order.driver_status}</dd></div>
      <div><dt>Support opened</dt><dd>${order.support_opened ? "Yes" : "No"}</dd></div>
      <div><dt>Previous intervention</dt><dd>${previousIntervention}</dd></div>
    </dl>
  `;
  detailEl.querySelector(".close-detail").addEventListener("click", () => {
    detailEl.hidden = true;
  });
}

async function showOrderDetail(orderId) {
  detailEl.hidden = false;
  detailEl.textContent = "Loading order details...";

  try {
    const response = await fetch(`/api/orders/${orderId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderDetail(await response.json());
  } catch (error) {
    detailEl.textContent = `Could not load order details: ${error.message}`;
  }
}

function renderOrders(orders) {
  if (orders.length === 0) {
    messageEl.textContent = "No active orders currently need attention.";
    ordersEl.innerHTML = "";
    return;
  }

  messageEl.textContent = `${orders.length} order${orders.length === 1 ? "" : "s"} need attention`;
  ordersEl.innerHTML = orders.map(orderCard).join("");

  document.querySelectorAll(".order-card").forEach((button) => {
    button.addEventListener("click", () => showOrderDetail(button.dataset.orderId));
  });
}

async function loadAtRiskOrders() {
  try {
    const response = await fetch("/api/orders/at-risk");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    renderOrders(await response.json());
  } catch (error) {
    messageEl.textContent = `Could not load at-risk orders: ${error.message}`;
    ordersEl.innerHTML = "";
  }
}

loadAtRiskOrders();
