const ordersEl = document.getElementById("orders");
const messageEl = document.getElementById("message");
const atRiskOrdersEl = document.getElementById("at-risk-orders");
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
    </button>
  `;
}

function bindOrderDetailClicks(container) {
  container.querySelectorAll(".order-card").forEach((button) => {
    button.addEventListener("click", () => {
      const orderId = button.dataset.orderId;
      window.alert(`Order detail is available at /api/orders/${orderId}`);
    });
  });
}

async function loadAtRiskOrders() {
  try {
    const response = await fetch("/api/at-risk-orders");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const orders = await response.json();
    if (orders.length === 0) {
      atRiskMessageEl.textContent = "No active orders currently need review.";
      atRiskOrdersEl.innerHTML = "";
      return;
    }

    atRiskMessageEl.textContent = `${orders.length} at-risk orders`;
    atRiskOrdersEl.innerHTML = orders.map(orderCard).join("");
    bindOrderDetailClicks(atRiskOrdersEl);
  } catch (error) {
    atRiskMessageEl.textContent = `Could not load at-risk orders: ${error.message}`;
  }
}

async function loadOrders() {
  try {
    const response = await fetch("/api/orders");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const orders = await response.json();
    messageEl.textContent = `${orders.length} orders loaded`;
    ordersEl.innerHTML = orders.map(orderCard).join("");
    bindOrderDetailClicks(ordersEl);
  } catch (error) {
    messageEl.textContent = `Could not load orders: ${error.message}`;
  }
}

loadAtRiskOrders();
loadOrders();
