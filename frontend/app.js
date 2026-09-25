const ordersEl = document.getElementById("orders");
const messageEl = document.getElementById("message");
const riskToggle = document.getElementById("risk-toggle");
const modal = document.getElementById("order-modal");
const modalBody = document.getElementById("modal-body");
const closeBtn = document.querySelector(".close-button");

riskToggle.addEventListener("change", loadOrders);

closeBtn.addEventListener("click", () => modal.classList.add("hidden"));
window.addEventListener("click", (e) => {
  if (e.target === modal) modal.classList.add("hidden");
});

function orderCard(order, index) {
  const delay = order.estimated_delay_minutes;
  const delayText = delay === null ? "Unknown delay" : `${delay} min`;
  const isRisk = order.status === "ACTIVE" && delay !== null && delay >= 10;
  
  // Highlighting with styled pill for delay
  const delayHtml = isRisk 
    ? `<span style="background: var(--danger-bg); color: #fca5a5; padding: 4px 10px; border-radius: 6px; font-weight: 700;">${delayText} Delay</span>` 
    : `<span class="meta">${delayText}</span>`;

  // Stagger animations
  const animDelay = (index * 0.05).toFixed(2);

  return `
    <button class="order-card" data-order-id="${order.order_id}" style="animation-delay: ${animDelay}s">
      <div>
        <strong class="order-id">${order.order_id}</strong>
        <span class="status-badge">${order.status}</span>
      </div>
      <div>
        <span class="meta">Promised ${order.promised_eta}</span>
        ${delayHtml}
      </div>
    </button>
  `;
}

async function loadOrders() {
  try {
    messageEl.textContent = "Loading orders…";
    const isRiskQueue = riskToggle.checked;
    const url = isRiskQueue ? "/api/orders?risk=true" : "/api/orders";
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const orders = await response.json();
    
    if (orders.length === 0 && isRiskQueue) {
      messageEl.textContent = "No orders currently at risk. You're all caught up!";
      ordersEl.innerHTML = "";
    } else {
      messageEl.textContent = `${orders.length} active orders loaded`;
      ordersEl.innerHTML = orders.map((o, i) => orderCard(o, i)).join("");
    }

    document.querySelectorAll(".order-card").forEach((button) => {
      button.addEventListener("click", () => {
        showOrderDetails(button.dataset.orderId);
      });
    });
  } catch (error) {
    messageEl.textContent = `Could not load orders: ${error.message}`;
  }
}

async function showOrderDetails(orderId) {
  modalBody.innerHTML = "<p>Loading details...</p>";
  modal.classList.remove("hidden");
  
  try {
    const response = await fetch(`/api/orders/${orderId}`);
    if (!response.ok) throw new Error("Failed to fetch order");
    const order = await response.json();
    
    const delay = order.estimated_delay_minutes;
    const delayText = delay === null ? "Unknown" : `${delay} min`;
    const delayColor = (delay !== null && delay >= 10) ? 'var(--danger)' : 'inherit';
    
    modalBody.innerHTML = `
      <h2 style="margin-top: 0; margin-bottom: 24px; color: var(--accent);">Order ${order.order_id}</h2>
      <div class="detail-row"><span class="detail-label">Status</span><span class="detail-value">${order.status}</span></div>
      <div class="detail-row"><span class="detail-label">Promised ETA</span><span class="detail-value">${order.promised_eta}</span></div>
      <div class="detail-row"><span class="detail-label">Current ETA</span><span class="detail-value">${order.current_eta || 'N/A'}</span></div>
      <div class="detail-row"><span class="detail-label">Estimated Delay</span><span class="detail-value" style="color: ${delayColor}">${delayText}</span></div>
      <div class="detail-row"><span class="detail-label">Restaurant</span><span class="detail-value">${order.restaurant_status}</span></div>
      <div class="detail-row"><span class="detail-label">Driver</span><span class="detail-value">${order.driver_status}</span></div>
      <div class="detail-row"><span class="detail-label">Support Ticket</span><span class="detail-value">${order.support_opened ? 'Opened' : 'None'}</span></div>
      ${order.previous_intervention ? `<div class="detail-row"><span class="detail-label">Intervention</span><span class="detail-value">${order.previous_intervention}</span></div>` : ''}
    `;
  } catch (err) {
    modalBody.innerHTML = `<p style="color: var(--danger)">Error loading details.</p>`;
  }
}

loadOrders();
