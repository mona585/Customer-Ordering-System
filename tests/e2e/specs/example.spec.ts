import { test, expect } from '@playwright/test';

test.describe('Local application smoke tests', () => {
  test('home page loads', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('body')).toBeVisible();
  });

  test('login page is reachable', async ({ page }) => {
    await page.goto('/auth/login');
    await expect(page.getByRole('button', { name: /sign\s*in|login/i })).toBeVisible();
  });
});
