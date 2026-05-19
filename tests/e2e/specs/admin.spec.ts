import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { AdminPage } from '../pages/AdminPage';

test.describe('Admin Gherkin Scenarios', () => {
    test('Scenario: Admin toggles menu availability and filters orders', async ({ page }) => {
        const loginPage = new LoginPage(page);
        const adminPage = new AdminPage(page);

        await test.step('Given the admin is logged in', async () => {
            await loginPage.navigate();
            // Using valid Admin credentials
            await loginPage.login('aura_admin', 'AdminPass!123');
            await loginPage.verifyRedirect('/admin/');
        });

        await test.step('When the admin goes to the Menu page and toggles an item', async () => {
            await adminPage.navigateToMenu();
            await adminPage.toggleFirstItemAvailability();
            await expect(page.locator('.alert-success')).toBeVisible(); // Assuming a flash message appears
        });

        await test.step('Then the admin can filter the orders dashboard by "CONFIRMED"', async () => {
            await adminPage.navigateToOrders();
            await adminPage.filterByStatus('CONFIRMED');
            await expect(page.url()).toContain('status=CONFIRMED');
        });
    });
});