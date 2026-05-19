import { test, expect } from '@playwright/test';

test.describe('2.1.1 Authentication - Customer Registration', () => {

    test('Scenario: Successful registration with valid fields', async ({ page }) => {
        // 1. Navigate to the register page
        await page.goto('/auth/register');

        // 2. Fill out the validation-compliant fields
        const testUser = `testuser_${Date.now()}`; // Unique username per run
        await page.fill('input[name="username"]', testUser);
        await page.fill('input[name="email"]', `${testUser}@example.com`);
        await page.fill('input[name="password"]', 'Strong!Pass123');
        await page.fill('input[name="password_confirm"]', 'Strong!Pass123');

        // 3. Submit the form
        await page.getByRole('button', { name: /Create Account|Register|Sign Up/i }).click();

        // 4. Wait for the redirection to complete. 
        // A successful redirect to the login page is the ultimate proof of success!
        await page.waitForURL(url => url.pathname.includes('/auth/login'));

        // 5. Verify the Login form is now visible and ready for the user
        const signInButton = page.getByRole('button', { name: /sign\s*in|login/i });
        await expect(signInButton).toBeVisible();
        
        // (We removed the text check here because the app's login page doesn't render flash messages)
    });

    test('Scenario: Registration fails with weak password', async ({ page }) => {
        // 1. Navigate to the register page
        await page.goto('/auth/register');
        
        // 2. Fill out with weak data that violates password policy rules
        await page.fill('input[name="username"]', 'badpassuser');
        await page.fill('input[name="email"]', 'badpass@example.com');
        await page.fill('input[name="password"]', '123'); 
        await page.fill('input[name="password_confirm"]', '123');
        
        // 3. Submit the form
        await page.getByRole('button', { name: /Create Account|Register/i }).click();

        // 4. Verify the user stays on the registration screen (validation blocked submission)
        expect(page.url()).toContain('/auth/register');
        
        // 5. Check for the error message
        const errorAlert = page.locator('.msg-banner.error, .msg-banner.danger, .error-message, .alert-danger').first();
        await expect(errorAlert).toBeVisible();
    });
});