const ordersEl = document.getElementById("orders");
const messageEl = document.getElementById("message");
const detailEl = document.getElementById("order-detail");

function orderCard(order) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "at-risk-card";
  button.dataset.orderId = order.order_id;
  button.innerHTML = `<strong></strong><span class="delay"></span>`;
  button.querySelector("strong").textContent = order.order_id;
  button.querySelector(".delay").textContent = `${order.estimated_delay_minutes} min delay`;
  button.addEventListener("click", () => showOrderDetail(order.order_id));
  return button;
}

function detailField(label, value) {
  const row = document.createElement("div");
  const name = document.createElement("dt");
  const content = document.createElement("dd");
  name.textContent = label;
  content.textContent = value == null ? "—" : String(value);
  row.append(name, content);
  return row;
}

async function showOrderDetail(orderId) {
  detailEl.hidden = false;
  detailEl.replaceChildren();
  const loading = document.createElement("p");
  loading.textContent = "Loading order details…";
  detailEl.append(loading);

  try {
    const response = await fetch(`/api/orders/${encodeURIComponent(orderId)}`);
    if (response.status === 404) {
      renderDetailMessage("Order not found", "This order may have been removed or is no longer available.");
      return;
    }
    if (!response.ok) throw new Error("Could not load order details. Please try again.");
    const order = await response.json();
    detailEl.replaceChildren();
    const heading = document.createElement("h2");
    heading.textContent = `Order ${order.order_id}`;
    const close = closeButton();
    const fields = document.createElement("dl");
    [
      ["Status", order.status], ["Promised ETA", order.promised_eta],
      ["Current ETA", order.current_eta], ["Estimated Delay", order.estimated_delay_minutes == null ? null : `${order.estimated_delay_minutes} min`],
      ["Restaurant Status", order.restaurant_status], ["Driver Status", order.driver_status],
      ["Support Opened", order.support_opened], ["Previous Intervention", order.previous_intervention],
    ].forEach(([label, value]) => fields.append(detailField(label, value)));
    detailEl.append(heading, close, fields);
  } catch (error) {
    renderDetailMessage("Could not load order", error.message);
  }
}

function closeButton() {
  const close = document.createElement("button");
  close.type = "button";
  close.className = "detail-close";
  close.textContent = "Close";
  close.addEventListener("click", () => { detailEl.hidden = true; });
  return close;
}

function renderDetailMessage(title, message) {
  detailEl.replaceChildren();
  const heading = document.createElement("h2");
  const body = document.createElement("p");
  heading.textContent = title;
  body.textContent = message;
  detailEl.append(heading, body, closeButton());
}

async function loadOrders() {
  try {
    const response = await fetch("/api/orders/at-risk");
    if (!response.ok) throw new Error("Could not load at-risk orders. Please refresh to try again.");
    const orders = await response.json();
    ordersEl.replaceChildren(...orders.map(orderCard));
    messageEl.textContent = orders.length ? `${orders.length} orders need attention` : "No at-risk orders right now.";
  } catch (error) {
    messageEl.textContent = error.message;
  }
}

loadOrders();
