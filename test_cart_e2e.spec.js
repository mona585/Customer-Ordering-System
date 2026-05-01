/**
 * test_cart_e2e.spec.js — End-to-End tests using Playwright + Page Object Model
 *
 * These tests cover the 10% E2E layer of the test pyramid.
 * They simulate real user interactions in a browser.
 *
 * Run: npx playwright test tests/test_cart_e2e.spec.js
 *
 * Corresponds to Gherkin scenarios in D3 Design Specification.
 */

const { test, expect } = require("@playwright/test");

// ─────────────────────────────────────────────
//  Page Object Model (POM) — Cart Page
// ─────────────────────────────────────────────
class CartPage {
  constructor(page) {
    this.page = page;
    this.cartTable      = page.locator("#cart-table");
    this.emptyMessage   = page.locator("#empty-msg");
    this.grandTotal     = page.locator("#grand-total");
    this.cartCount      = page.locator("#cart-count");
    this.clearBtn       = page.locator("button:has-text('Clear Cart')");
    this.checkoutLink   = page.locator("a:has-text('Proceed to Checkout')");
    this.toast          = page.locator("#toast");
  }

  async goto() {
    await this.page.goto("http://localhost:5000/cart/");
  }

  // Locators for a specific product row
  qtyValue(productId)   { return this.page.locator(`#qty-${productId}`); }
  lineTotal(productId)  { return this.page.locator(`#line-${productId}`); }
  qtyIncBtn(productId)  { return this.page.locator(`#row-${productId} button:has-text('+')`); }
  qtyDecBtn(productId)  { return this.page.locator(`#row-${productId} button:has-text('−')`); }
  removeBtn(productId)  { return this.page.locator(`#row-${productId} .remove-btn`); }

  async getGrandTotal() {
    const text = await this.grandTotal.textContent();
    return parseFloat(text.replace("$", ""));
  }
}

// ─────────────────────────────────────────────
//  Helper: seed a cart item via API
// ─────────────────────────────────────────────
async function addItemToCart(request, item) {
  await request.post("http://localhost:5000/cart/add", {
    data: item,
    headers: { "Content-Type": "application/json" },
  });
}

// ─────────────────────────────────────────────
//  TEST SUITE
// ─────────────────────────────────────────────

test.describe("Cart System — E2E Tests", () => {

  test.beforeEach(async ({ request }) => {
    // Clear cart before each test for isolation
    await request.post("http://localhost:5000/cart/clear", { data: {} });
  });

  // ── Scenario: View empty cart ──────────────────
  // Given the user is logged in
  // When they navigate to /cart/
  // Then they see the "Your cart is empty" message
  test("shows empty state when cart has no items", async ({ page }) => {
    const cartPage = new CartPage(page);
    await cartPage.goto();
    await expect(cartPage.emptyMessage).toBeVisible();
    await expect(cartPage.cartTable).not.toBeVisible();
  });

  // ── Scenario: View cart with items ────────────────
  // Given user has added 2 items to the cart
  // When they visit the cart page
  // Then both items and the correct total are displayed
  test("displays items and correct total when cart is populated", async ({ page, request }) => {
    await addItemToCart(request, {
      product_id: 1, product_name: "Burger", product_price: 9.99, quantity: 2,
    });
    await addItemToCart(request, {
      product_id: 2, product_name: "Cola", product_price: 1.50, quantity: 1,
    });

    const cartPage = new CartPage(page);
    await cartPage.goto();

    await expect(cartPage.cartTable).toBeVisible();
    await expect(cartPage.qtyValue(1)).toHaveText("2");
    await expect(cartPage.qtyValue(2)).toHaveText("1");

    const total = await cartPage.getGrandTotal();
    expect(total).toBeCloseTo(21.48, 2); // 9.99*2 + 1.50
  });

  // ── Scenario: Increment item quantity ─────────────
  // Given user has a Burger (qty=1) in cart
  // When they click the + button
  // Then quantity becomes 2 and total updates
  test("increments quantity when + is clicked", async ({ page, request }) => {
    await addItemToCart(request, {
      product_id: 1, product_name: "Burger", product_price: 9.99, quantity: 1,
    });

    const cartPage = new CartPage(page);
    await cartPage.goto();
    await cartPage.qtyIncBtn(1).click();

    await expect(cartPage.qtyValue(1)).toHaveText("2");
    const total = await cartPage.getGrandTotal();
    expect(total).toBeCloseTo(19.98, 2);
  });

  // ── Scenario: Remove item ────────────────────────
  // Given user has an item in cart
  // When they click ✕
  // Then the row is removed and total updates
  test("removes item when remove button is clicked", async ({ page, request }) => {
    await addItemToCart(request, {
      product_id: 3, product_name: "Fries", product_price: 3.50, quantity: 1,
    });

    const cartPage = new CartPage(page);
    await cartPage.goto();
    await cartPage.removeBtn(3).click();

    // Row should disappear
    await expect(page.locator("#row-3")).not.toBeVisible();
  });

  // ── Scenario: Clear cart ─────────────────────────
  // Given user has items in cart
  // When they click "Clear Cart" and confirm
  // Then cart becomes empty
  test("clears all items when Clear Cart is clicked", async ({ page, request }) => {
    await addItemToCart(request, {
      product_id: 1, product_name: "Burger", product_price: 9.99, quantity: 1,
    });

    const cartPage = new CartPage(page);
    await cartPage.goto();

    // Handle the confirm() dialog
    page.on("dialog", dialog => dialog.accept());
    await cartPage.clearBtn.click();

    await expect(cartPage.emptyMessage).toBeVisible({ timeout: 3000 });
  });

  // ── Scenario: Checkout button visible ─────────────
  test("checkout link is visible when cart has items", async ({ page, request }) => {
    await addItemToCart(request, {
      product_id: 1, product_name: "Burger", product_price: 9.99, quantity: 1,
    });

    const cartPage = new CartPage(page);
    await cartPage.goto();
    await expect(cartPage.checkoutLink).toBeVisible();
  });

  // ── Scenario: Decrement to zero removes item ──────
  // Given user has item with quantity=1
  // When they click − (decrement)
  // Then item is removed from cart
  test("removes item when quantity is decremented below 1", async ({ page, request }) => {
    await addItemToCart(request, {
      product_id: 5, product_name: "Tea", product_price: 2.00, quantity: 1,
    });

    const cartPage = new CartPage(page);
    await cartPage.goto();
    await cartPage.qtyDecBtn(5).click();

    await expect(page.locator("#row-5")).not.toBeVisible({ timeout: 2000 });
  });

});
