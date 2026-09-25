const ordersEl = document.getElementById("orders");
const messageEl = document.getElementById("message");

function orderCard(order) {
  const delay = order.estimated_delay_minutes;
  const delayText = delay === null ? "Unknown delay" : delay < 0 ? "Invalid delay" : `${delay} min`;
  const supportText = order.support_opened ? "Support ticket open" : "No support ticket";

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
        <span>${supportText}</span>
      </div>
    </button>
  `;
}

async function loadOrders() {
  try {
    const response = await fetch("/api/orders?at_risk=true");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const orders = await response.json();

    if (orders.length === 0) {
      messageEl.textContent = "No at-risk orders right now.";
      ordersEl.innerHTML = "<div class=\"empty-state\">No at-risk orders currently require intervention.</div>";
      return;
    }

    const countLabel = orders.length === 1 ? "1 at-risk order loaded" : `${orders.length} at-risk orders loaded`;
    messageEl.textContent = countLabel;
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

loadOrders();
