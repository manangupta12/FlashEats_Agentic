const atRiskOrdersEl = document.getElementById("at-risk-orders");
const atRiskMessageEl = document.getElementById("at-risk-message");
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

function renderOrderDetail(order) {
  const delayLabel = order.estimated_delay_minutes === null
    ? "Unknown delay"
    : `${order.estimated_delay_minutes} min`;
  const currentEta = order.current_eta || "Not available";
  const previousAction = order.previous_intervention || "None";

  detailEl.hidden = false;
  detailEl.innerHTML = `
    <div class="detail-head">
      <div>
        <p class="eyebrow">ORDER DETAIL</p>
        <h2>${order.order_id}</h2>
      </div>
      <button class="detail-close" type="button">Hide</button>
    </div>
    <dl class="detail-grid">
      <div><dt>Status</dt><dd>${order.status}</dd></div>
      <div><dt>Delay</dt><dd>${delayLabel}</dd></div>
      <div><dt>Promised ETA</dt><dd>${order.promised_eta}</dd></div>
      <div><dt>Current ETA</dt><dd>${currentEta}</dd></div>
      <div><dt>Restaurant</dt><dd>${order.restaurant_status}</dd></div>
      <div><dt>Driver</dt><dd>${order.driver_status}</dd></div>
      <div><dt>Support opened</dt><dd>${order.support_opened ? "Yes" : "No"}</dd></div>
      <div><dt>Previous intervention</dt><dd>${previousAction}</dd></div>
    </dl>
  `;
  detailEl.querySelector(".detail-close").addEventListener("click", () => {
    detailEl.hidden = true;
  });
}

async function loadOrderDetail(orderId) {
  detailEl.hidden = false;
  detailEl.textContent = "Loading order details...";

  try {
    const response = await fetch(`/api/orders/${orderId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderOrderDetail(await response.json());
  } catch (error) {
    detailEl.textContent = `Could not load order details: ${error.message}`;
  }
}

function attachCardClicks(container) {
  container.querySelectorAll(".order-card").forEach((button) => {
    button.addEventListener("click", () => loadOrderDetail(button.dataset.orderId));
  });
}

function renderOrderCollection(container, messageContainer, orders, emptyText, countTextFactory) {
  if (orders.length === 0) {
    container.innerHTML = "";
    messageContainer.textContent = emptyText;
    return;
  }

  container.innerHTML = orders.map(orderCard).join("");
  messageContainer.textContent = countTextFactory(orders.length);
  attachCardClicks(container);
}

async function loadAtRiskOrders() {
  try {
    const response = await fetch("/api/orders/at-risk");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    renderOrderCollection(
      atRiskOrdersEl,
      atRiskMessageEl,
      await response.json(),
      "No at-risk orders at this time.",
      (count) => `${count} order${count === 1 ? "" : "s"} need attention`
    );
  } catch (error) {
    atRiskOrdersEl.innerHTML = "";
    atRiskMessageEl.textContent = `Could not load at-risk orders: ${error.message}`;
  }
}

async function loadOrders() {
  try {
    const response = await fetch("/api/orders");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    renderOrderCollection(
      ordersEl,
      messageEl,
      await response.json(),
      "No orders found.",
      (count) => `${count} orders loaded`
    );
  } catch (error) {
    ordersEl.innerHTML = "";
    messageEl.textContent = `Could not load orders: ${error.message}`;
  }
}

loadAtRiskOrders();
loadOrders();
