import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { MenuPage } from '../pages/MenuPage';
import { CartPage } from '../pages/CartPage'; // 🌟 Import from its own file

test.describe('Customer Gherkin Scenarios', () => {
    test('Scenario: Customer successfully places a discounted order', async ({ page }) => {
        const loginPage = new LoginPage(page);
        const menuPage = new MenuPage(page);
        const cartPage = new CartPage(page);

        await test.step('Given the customer is logged in', async () => {
            await loginPage.navigate();
            await loginPage.login('kerokhairy15@gmail.com', 'Test@105');
            await loginPage.verifyRedirect('/customer/');
        });

        await test.step('When they browse the menu and add an item to the cart', async () => {
            await menuPage.navigate();
            await menuPage.addFirstItemToCart();
        });

        await test.step('And they navigate to the cart and apply promo "SAVE10"', async () => {
            await cartPage.navigate();
            await cartPage.applyPromo('SAVE10');
        });

        await test.step('Then the totals should be updated and order proceeds to checkout', async () => {
            await cartPage.verifyDiscountApplied();
            await page.click('a:has-text("Proceed to Checkout")');
            await expect(page).toHaveURL(/.*\/customer\/checkout/);
        });
    });
});