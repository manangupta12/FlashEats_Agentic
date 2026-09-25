const atRiskEl = document.getElementById("at-risk-orders");
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

function bindOrderCards(container) {
  container.querySelectorAll(".order-card").forEach((button) => {
    button.addEventListener("click", () => showOrderDetail(button.dataset.orderId));
  });
}

function renderList(container, listMessageEl, orders, emptyText, countText) {
  if (orders.length === 0) {
    listMessageEl.textContent = emptyText;
    container.innerHTML = "";
    return;
  }

  listMessageEl.textContent = countText(orders.length);
  container.innerHTML = orders.map(orderCard).join("");
  bindOrderCards(container);
}

async function loadAtRiskOrders() {
  try {
    const response = await fetch("/api/orders/at-risk");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    renderList(
      atRiskEl,
      atRiskMessageEl,
      await response.json(),
      "No at-risk orders right now.",
      (count) => `${count} order${count === 1 ? "" : "s"} need attention`
    );
  } catch (error) {
    atRiskMessageEl.textContent = `Could not load at-risk orders: ${error.message}`;
    atRiskEl.innerHTML = "";
  }
}

async function loadOrders() {
  try {
    const response = await fetch("/api/orders");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    renderList(
      ordersEl,
      messageEl,
      await response.json(),
      "No orders found.",
      (count) => `${count} orders loaded`
    );
  } catch (error) {
    messageEl.textContent = `Could not load orders: ${error.message}`;
    ordersEl.innerHTML = "";
  }
}

loadAtRiskOrders();
loadOrders();
