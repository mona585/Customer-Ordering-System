/**
 * cart.js — Frontend logic for the Cart page.
 */

// ─────────────────────────────────────────────
//  Toast helper
// ─────────────────────────────────────────────
function showToast(msg, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className = `toast ${type}`;
  setTimeout(() => { toast.className = "toast hidden"; }, 2500);
}

// ─────────────────────────────────────────────
//  Change Quantity — Unlimited, − removes 1 at a time
// ─────────────────────────────────────────────
async function changeQty(productId, newQty) {
  if (newQty < 1) {
    return removeItem(productId);
  }

  try {
    const res = await fetch("/cart/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: newQty }),
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || "Update failed", "error");
      return;
    }

   
    document.getElementById(`qty-${productId}`).textContent = newQty;

    const row = document.getElementById(`row-${productId}`);
    if (row) {
      const minusBtn = row.querySelector(".qty-btn:first-child");
      const plusBtn  = row.querySelector(".qty-btn:last-child");
      if (minusBtn) minusBtn.setAttribute("onclick", `changeQty(${productId}, ${newQty - 1})`);
      if (plusBtn)  plusBtn.setAttribute("onclick",  `changeQty(${productId}, ${newQty + 1})`);
    }

    await refreshCartSummary(data);
    showToast("Quantity updated");
  } catch {
    showToast("Network error", "error");
  }
}

// ─────────────────────────────────────────────
//  Remove Item 
// ─────────────────────────────────────────────
async function removeItem(productId) {
  try {
    const res = await fetch("/cart/remove", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId }),
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || "Remove failed", "error");
      return;
    }

    const row = document.getElementById(`row-${productId}`);
    if (row) {
      row.style.transition = "opacity 0.3s";
      row.style.opacity = "0";
      setTimeout(() => row.remove(), 300);
    }

    await refreshCartSummary(data);
    showToast("Item removed");

    if (data.cart_count === 0) {
      setTimeout(() => location.reload(), 400);
    }
  } catch {
    showToast("Network error", "error");
  }
}

// ─────────────────────────────────────────────
//  Clear Cart
// ─────────────────────────────────────────────
async function clearCart() {
  if (!confirm("Are you sure you want to clear your entire cart?")) return;

  try {
    const res = await fetch("/cart/clear", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.error || "Clear failed", "error");
      return;
    }

    showToast("Cart cleared");
    setTimeout(() => location.reload(), 500);
  } catch {
    showToast("Network error", "error");
  }
}

// ─────────────────────────────────────────────
//  Refresh summary
// ─────────────────────────────────────────────
async function refreshCartSummary(data) {
  const totalEl = document.getElementById("grand-total");
  const countEl = document.getElementById("cart-count");

  if (data.cart_total !== undefined && totalEl) {
    totalEl.textContent = `$${data.cart_total.toFixed(2)}`;
  }
  if (data.cart_count !== undefined && countEl) {
    countEl.textContent = data.cart_count;
  }

  const res = await fetch("/cart/api");
  const cartData = await res.json();
  if (cartData.cart && cartData.cart.items) {
    cartData.cart.items.forEach(item => {
      const lineEl = document.getElementById(`line-${item.product_id}`);
      if (lineEl) lineEl.textContent = `$${item.line_total.toFixed(2)}`;
    });
  }
}

const CartAPI = {
  async addItem(product) {
    const res = await fetch("/cart/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(product),
    });
    return res.json();
  }
};