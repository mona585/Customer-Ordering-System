/**
 * cart.js — Frontend logic for the Cart page.
 *
 * Communicates with the Flask backend via fetch() API calls.
 * All functions update the DOM without a full page reload.
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
//  Change Quantity
// ─────────────────────────────────────────────
async function changeQty(productId, newQty) {
  if (newQty < 1) {
    // Removing the item entirely when user clicks − on qty=1
    return removeItem(productId);
  }
  if (newQty > 99) {
    showToast("Max 99 per item", "error");
    return;
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

    // Update quantity display
    document.getElementById(`qty-${productId}`).textContent = newQty;

    // Recalculate line total (we need the price; get it from the refreshed cart)
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

    // Animate row removal
    const row = document.getElementById(`row-${productId}`);
    if (row) {
      row.style.transition = "opacity 0.3s";
      row.style.opacity = "0";
      setTimeout(() => row.remove(), 300);
    }

    await refreshCartSummary(data);
    showToast("Item removed");

    // Show empty state if nothing left
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
//  Refresh summary section (count + total)
// ─────────────────────────────────────────────
async function refreshCartSummary(data) {
  // Backend returns cart_total and cart_count directly on update/remove
  const totalEl = document.getElementById("grand-total");
  const countEl = document.getElementById("cart-count");

  if (data.cart_total !== undefined && totalEl) {
    totalEl.textContent = `$${data.cart_total.toFixed(2)}`;
  }
  if (data.cart_count !== undefined && countEl) {
    countEl.textContent = data.cart_count;
  }

  // Refresh per-line totals from the API
  const res = await fetch("/cart/api");
  const cartData = await res.json();
  if (cartData.cart && cartData.cart.items) {
    cartData.cart.items.forEach(item => {
      const lineEl = document.getElementById(`line-${item.product_id}`);
      if (lineEl) lineEl.textContent = `$${item.line_total.toFixed(2)}`;
    });
  }
}

/**
 * PUBLIC function — can be called from the Product page's "Add to Cart" button.
 * Example usage on product page:
 *   CartAPI.addItem({ product_id: 5, product_name: "Burger", product_price: 8.99, quantity: 1 });
 */
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
