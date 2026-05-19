import { Page, expect } from '@playwright/test';

export type DeliveryAdvanceResult = 'advanced' | 'no-actionable-orders';

export class DeliveryPage {
    constructor(private readonly page: Page) {}

    async navigate() {
        await this.page.goto('/delivery/');
        await expect(this.page).toHaveURL(/\/delivery\/?/);
    }

    async advanceFirstOrderStatus(): Promise<DeliveryAdvanceResult> {
        const statusButton = this.page
            .locator('table.admin-table form button[type="submit"].admin-btn.admin-btn-primary')
            .filter({ hasText: /Mark Out for Delivery|Mark Delivered/i })
            .first();

        if ((await statusButton.count()) === 0) {
            return 'no-actionable-orders';
        }

        await expect(statusButton).toBeVisible();

        const [postResponse] = await Promise.all([
            this.page.waitForResponse(
                response =>
                    response.request().method() === 'POST' &&
                    response.url().includes('/delivery')
            ),
            statusButton.click(),
        ]);

        expect([200, 301, 302, 303]).toContain(postResponse.status());
        await this.page.waitForLoadState('domcontentloaded');

        return 'advanced';
    }

    async expectNoActionableDeliveryOrder() {
        const emptyQueue = this.page.getByText(/No orders in the delivery queue/i);
        const completedOrderMarker = this.page.getByText(/^Done$/i);

        if ((await emptyQueue.count()) > 0) {
            await expect(emptyQueue.first()).toBeVisible();
            return;
        }

        await expect(completedOrderMarker.first()).toBeVisible();
    }
}