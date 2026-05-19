import { Page, expect } from '@playwright/test';

export class LoginPage {
    constructor(private page: Page) {}

    async navigate() {
        await this.page.goto('/auth/login');
    }

    async login(identifier: string, password: string = 'TestPass!123') {
        await this.page.fill('input[name="identifier"]', identifier);
        await this.page.fill('input[name="password"]', password);
        
        // 🌟 Fix: Uses the accessible name role to catch the button 
        // safely even if the JavaScript changes the text to "Authenticating…"
        await this.page.getByRole('button', { name: /sign\s*in/i }).click();
    }

    async verifyRedirect(expectedUrlPart: string) {
        // 🌟 Fix: Safe URL validation matching using an explicit predicate function
        await this.page.waitForURL(url => url.href.includes(expectedUrlPart));
        expect(this.page.url()).toContain(expectedUrlPart);
    }
}