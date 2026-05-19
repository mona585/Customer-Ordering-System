import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DeliveryPage, DeliveryAdvanceResult } from '../pages/DeliveryPage';

test.describe('Delivery Gherkin Scenarios', () => {
    test('Scenario: Driver advances an available delivery order, or sees a valid empty queue state', async ({ page }) => {
        const loginPage = new LoginPage(page);
        const deliveryPage = new DeliveryPage(page);
        let result: DeliveryAdvanceResult;

        await test.step('Given the delivery driver is logged in', async () => {
            await loginPage.navigate();
            await loginPage.login('aura_delivery', 'DeliveryPass!123');
            await loginPage.verifyRedirect('/delivery/');
        });

        await test.step('When they view the delivery dashboard', async () => {
            result = await deliveryPage.advanceFirstOrderStatus();
        });

        await test.step('Then the order is advanced when one is available, otherwise the dashboard shows a valid non-actionable state', async () => {
            if (result === 'advanced') {
                await expect(page.locator('.alert-success')).toContainText(/status updated/i);
                return;
            }

            await deliveryPage.expectNoActionableDeliveryOrder();
        });
    });
});