import { Page, expect } from '@playwright/test';

export class CartPage {
    constructor(private readonly page: Page) {}

    async navigate() {
        await this.page.goto('/customer/cart');
        await expect(this.page).toHaveURL(/\/customer\/cart/);
    }

    async applyPromo(code: string) {
        const promoInput = this.page.locator('input[name="promo_code"]');
        const applyButton = this.page.getByRole('button', { name: /apply/i });

        await expect(promoInput).toBeVisible();
        await promoInput.fill(code);
        await expect(applyButton).toBeVisible();
        await applyButton.click();
    }

    async verifyDiscountApplied() {
        const successMsg = this.page.locator('.promo-msg');
        await expect(successMsg).toBeVisible();
        await expect(successMsg).toContainText(/code applied successfully/i);
    }
}
