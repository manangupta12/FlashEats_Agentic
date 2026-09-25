const ordersEl = document.getElementById("orders");
const messageEl = document.getElementById("message");
const atRiskEl = document.getElementById("at-risk-orders");
const atRiskMessageEl = document.getElementById("at-risk-message");

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
      <div>
        <span>${order.restaurant_status}</span>
        <span>${order.driver_status}</span>
      </div>
    </button>
  `;
}

function bindOrderCards(container) {
  container.querySelectorAll(".order-card").forEach((button) => {
    button.addEventListener("click", () => {
      window.alert(`Order detail is available at /api/orders/${button.dataset.orderId}`);
    });
  });
}

async function loadOrders() {
  try {
    const response = await fetch("/api/orders");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const orders = await response.json();
    messageEl.textContent = `${orders.length} orders loaded`;
    ordersEl.innerHTML = orders.map(orderCard).join("");

    bindOrderCards(ordersEl);
  } catch (error) {
    messageEl.textContent = `Could not load orders: ${error.message}`;
  }
}

async function loadAtRiskOrders() {
  try {
    const response = await fetch("/api/orders/at-risk");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const orders = await response.json();
    atRiskEl.innerHTML = orders.map(orderCard).join("");
    atRiskMessageEl.textContent = orders.length
      ? `${orders.length} at-risk orders`
      : "No at-risk orders right now";
    bindOrderCards(atRiskEl);
  } catch (error) {
    atRiskMessageEl.textContent = `Could not load at-risk orders: ${error.message}`;
  }
}

loadAtRiskOrders();
loadOrders();
