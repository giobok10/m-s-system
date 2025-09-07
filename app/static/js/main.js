// Main JavaScript file for restaurant system

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));

  // Auto-hide alerts after 5 seconds
  setTimeout(() => {
    document.querySelectorAll(".alert").forEach((alert) => {
      new bootstrap.Alert(alert).close();
    });
  }, 5000);

  // Handle cook's actions without page reload
  document.getElementById('orders-container')?.addEventListener('click', function(e) {
    const form = e.target.closest('form');
    if (form) {
        e.preventDefault();
        const button = form.querySelector('button[type="submit"]');
        const restore = showLoading(button);

        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                showNotification(data.message || 'Ocurrió un error', 'danger');
                restore(); // Restore button state only on server-side failure
            }
            // On success, the button state will be updated by the WebSocket event.
            // The loading spinner will remain until the WebSocket event is processed.
        })
        .catch(() => {
            showNotification('Error de conexión', 'danger');
            restore(); // Restore button state on network error
        });
    }
  });
});

// Utility function for loading state on buttons
function showLoading(button) {
  const originalText = button.innerHTML;
  button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Cargando...';
  button.disabled = true;
  return () => {
    button.innerHTML = originalText;
    button.disabled = false;
  };
}

// Global notification function
function showNotification(message, type = "info") {
  const alertContainer = document.createElement('div');
  alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  alertContainer.style.cssText = "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
  alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
  document.body.appendChild(alertContainer);
  playNotificationSound(); // Play sound on notification
  setTimeout(() => new bootstrap.Alert(alertContainer).close(), 5000);
}

// Function to play notification sound
function playNotificationSound() {
  const audio = new Audio('/static/notification.mp3');
  audio.play().catch(error => console.error("Audio playback failed:", error));
}


// --- WebSocket Connection and Event Handlers ---
if (typeof io !== "undefined") {
  const socket = io({ path: '/socket.io/' });

  socket.on("connect", () => {
    console.log("Connected to WebSocket server");
  });

  socket.on("disconnect", () => {
    console.log("Disconnected from WebSocket server");
  });

  // --- Event Handlers ---

  socket.on('new_order', (data) => {
    const ordersContainer = document.getElementById('orders-container');
    if (ordersContainer) {
        showNotification(`Nueva orden #${data.order_id} para ${data.customer_name}`, 'info');
        const noOrdersMessage = ordersContainer.querySelector('.text-center');
        if (noOrdersMessage) {
            noOrdersMessage.parentElement.remove();
        }
        ordersContainer.insertAdjacentHTML('afterbegin', createNewOrderCard(data));
    }
  });

  socket.on('order_status_update', (data) => {
    const message = `La orden #${data.order_id} (${data.customer_name}) está ${data.status.replace(/_/g, ' ')}.`;
    showNotification(message, 'success');
    
    // Update for Waiter's Dashboard
    updateWaiterOrderStatus(data.order_id, data.status);
    
    // Update for Cook's Dashboard
    updateCookOrderStatus(data.order_id, data.status);
  });

  socket.on('stock_update', (data) => {
    // Update stock on "Take Order" page
    const productCard = document.querySelector(`.product-card[data-product-id="${data.product_id}"]`);
    if (productCard) {
        productCard.dataset.productStock = data.stock;
        const stockSmallElement = productCard.querySelector(`small[data-stock-id="${data.product_id}"]`);
        if (stockSmallElement) {
            stockSmallElement.textContent = `Stock: ${data.stock}`;
            stockSmallElement.className = `text-${data.stock > 5 ? 'success' : data.stock > 0 ? 'warning' : 'danger'}`;
            productCard.querySelector('.add-product').disabled = data.stock <= 0;
        }
    }
    const extraCheckbox = document.querySelector(`.extra-checkbox[value="${data.product_id}"]`);
    if (extraCheckbox) {
        extraCheckbox.dataset.extraStock = data.stock;
        const stockSmallElement = extraCheckbox.nextElementSibling.querySelector(`small[data-stock-id="${data.product_id}"]`);
        if (stockSmallElement) {
            stockSmallElement.textContent = `(${data.stock <= 0 ? 'Agotado' : 'Stock: ' + data.stock})`;
            extraCheckbox.disabled = data.stock <= 0;
        }
    }

    // Update stock on Cook's "Stock" page
    const stockRow = document.querySelector(`tr[data-product-id="${data.product_id}"]`);
    if (stockRow) {
        const stockSpan = stockRow.querySelector('.stock-level');
        if (stockSpan) {
            stockSpan.textContent = data.stock;
            stockSpan.className = `badge fs-6 stock-level bg-${data.stock == 0 ? 'danger' : data.stock <= 5 ? 'warning' : 'success'}`;
        }
    }
  });

}

// --- UI Update Functions ---

function createNewOrderCard(data) {
    let itemsHtml = '';
    data.items.forEach(item => {
        let extrasText = '';
        if (item.extras && item.extras !== '[]') {
            try {
                const extrasList = JSON.parse(item.extras);
                extrasText = extrasList.map(e => `${e.name} (x${e.quantity})`).join(', ');
            } catch(e) { extrasText = item.extras; } // Fallback for non-json
        }

        itemsHtml += `
            <div class="mb-2">
                <div><strong>${item.quantity}x ${item.product_name}</strong></div>
                <div class="ps-2">
                    ${extrasText ? `<small class="text-primary d-block">Extras: ${extrasText}</small>` : ''}
                    ${item.notes ? `<small class="text-warning d-block">Notas: ${item.notes}</small>` : ''}
                </div>
            </div>
        `;
    });

    return `
        <div class="col-md-6 col-lg-4 mb-4" id="order-card-${data.order_id}">
            <div class="card border-warning">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">Orden #${data.order_id}</h6>
                    <span class="badge bg-warning">Nueva</span>
                </div>
                <div class="card-body">
                    <p><strong>Cliente:</strong> ${data.customer_name || 'Sin nombre'}</p>
                    <p><strong>Hora:</strong> ${new Date().toLocaleTimeString('es-GT', { hour: '2-digit', minute: '2-digit' })}</p>
                    <hr>
                    <h6>Productos:</h6>
                    ${itemsHtml}
                    <hr>
                    <div class="d-grid gap-2">
                        <form method="POST" action="/cook/start_preparation/${data.order_id}">
                            <button type="submit" class="btn btn-warning w-100">
                                <i class="fas fa-play"></i> Iniciar Preparación
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function updateWaiterOrderStatus(orderId, status) {
    const orderCard = document.getElementById(`order-card-${orderId}`);
    if (!orderCard || !orderCard.querySelector('a[href*="waiter"]')) return; // Only run on waiter's dashboard

    const statusBadge = orderCard.querySelector('.badge');
    const card = orderCard.querySelector('.card');
    const actions = orderCard.querySelector('.d-grid');

    const statusMap = {
        'in_preparation': { text: 'En Preparación', badge: 'bg-info', border: 'border-info' },
        'ready': { text: 'Ready', badge: 'bg-success', border: 'border-success' }
    };

    const newStatus = statusMap[status];
    if (!newStatus) return;

    if (statusBadge) {
        statusBadge.textContent = newStatus.text;
        statusBadge.className = `badge ${newStatus.badge}`;
    }
    if (card) {
        card.className = `card ${newStatus.border}`;
    }
    if (status === 'ready' && actions && !actions.querySelector('a[href*="process_payment"]')) {
        const paymentButton = `
            <a href="/waiter/process_payment/${orderId}" class="btn btn-success btn-sm mt-2">
                <i class="fas fa-cash-register"></i> Procesar Pago
            </a>
        `;
        actions.insertAdjacentHTML('beforeend', paymentButton);
    }
}

function updateCookOrderStatus(orderId, status) {
    const orderCard = document.getElementById(`order-card-${orderId}`);
    if (!orderCard || !orderCard.querySelector('form[action*="cook"]')) return; // Only run on cook's dashboard

    if (status === 'ready') {
        orderCard.remove();
        // Check if container is empty
        const container = document.getElementById('orders-container');
        if (container && container.children.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="text-center py-5">
                        <i class="fas fa-fire fa-3x text-muted mb-3"></i>
                        <h4 class="text-muted">No hay órdenes pendientes</h4>
                        <p class="text-muted">Las órdenes aparecerán aquí cuando los meseros las envíen</p>
                    </div>
                </div>
            `;
        }
        return;
    }
    
    if (status === 'in_preparation') {
        const card = orderCard.querySelector('.card');
        const statusBadge = orderCard.querySelector('.badge');
        const form = orderCard.querySelector('form');

        if (card) card.className = 'card border-info';
        if (statusBadge) {
            statusBadge.textContent = 'En Preparación';
            statusBadge.className = 'badge bg-info';
        }
        if (form) {
            const button = form.querySelector('button');
            form.action = `/cook/mark_ready/${orderId}`;
            button.className = 'btn btn-success w-100';
            button.innerHTML = '<i class="fas fa-check"></i> Marcar como Listo';
            button.disabled = false; // Re-enable the button
        }
    }
}