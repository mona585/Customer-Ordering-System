import { Page, expect } from '@playwright/test';

export class MenuPage {
    constructor(private readonly page: Page) {}

    async navigate() {
        await this.page.goto('/customer/menu');
        await expect(this.page).toHaveURL(/\/customer\/menu/);
        await expect(this.page.locator('.menu-grid').first()).toBeVisible();
    }

    async addFirstItemToCart() {
        // home.html renders authenticated, in-stock menu actions as:
        // <button class="add-btn" title="Add to Cart">+</button>
        const addButton = this.page
            .locator('button.add-btn[title="Add to Cart"]:not([disabled])')
            .first();

        await expect(addButton).toBeVisible();

        const [response] = await Promise.all([
            this.page.waitForResponse(
                res =>
                    res.url().includes('/customer/api/cart/add') &&
                    res.request().method() === 'POST'
            ),
            addButton.click(),
        ]);

        expect(response.ok()).toBeTruthy();

        const body = await response.json();
        expect(body.success).toBeTruthy();
    }
}