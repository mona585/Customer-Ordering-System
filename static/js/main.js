// main.js — Products page logic

function showToast(msg, type = "success") {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className = `toast ${type}`;
  setTimeout(() => { toast.className = "toast hidden"; }, 2500);
}

async function addToCart(productId, name, price, btn) {
  btn.disabled = true;
  btn.textContent = "Adding...";
  try {
    const res = await fetch("/cart/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, product_name: name, product_price: price, quantity: 1 })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || "Failed to add", "error");
      btn.disabled = false;
      btn.textContent = "Add to Cart";
      return;
    }
    btn.textContent = "Added!";
    btn.classList.add("added");
    showToast(`${name} added to cart!`);
    updateNavBadge();
    setTimeout(() => {
      btn.textContent = "Add to Cart";
      btn.classList.remove("added");
      btn.disabled = false;
    }, 1500);
  } catch {
    showToast("Network error", "error");
    btn.disabled = false;
    btn.textContent = "Add to Cart";
  }
}

async function updateNavBadge() {
  try {
    const res = await fetch("/cart/api");
    const data = await res.json();
    const badge = document.getElementById("nav-count");
    if (badge && data.cart) badge.textContent = data.cart.item_count;
  } catch {}
}

updateNavBadge();
