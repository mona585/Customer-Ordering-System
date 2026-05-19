import { Page, expect } from '@playwright/test';

export class AdminPage {
    constructor(private page: Page) {}

    async navigateToMenu() {
        await this.page.goto('/admin/menu');
    }

    async toggleFirstItemAvailability() {
        // 🌟 CHANGE THIS LINE: Look for the button with the text "Toggle"
        const toggleBtn = this.page.locator('button:has-text("Toggle")').first();
        await toggleBtn.click();
    }

    async navigateToOrders() {
        await this.page.goto('/admin/orders');
    }

    async filterByStatus(status: string) {
        // 1. Target the correct select element name "status"
        await this.page.selectOption('select[name="status"]', status);
        
        // 2. Do NOT look for a "Filter" button since the form auto-submits on change!
        // Instead, wait for the URL or navigation to update.
        await this.page.waitForURL(url => url.href.includes(`status=${status}`));
    }
}