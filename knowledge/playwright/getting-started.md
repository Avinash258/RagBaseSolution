# Playwright Getting Started

Playwright is an end-to-end testing framework for modern web apps. It supports Chromium, Firefox, and WebKit with one API.

## Install

```bash
npm init playwright@latest
# or
npm i -D @playwright/test
npx playwright install
```

## First test

```ts
import { test, expect } from '@playwright/test';

test('homepage has title', async ({ page }) => {
  await page.goto('https://playwright.dev/');
  await expect(page).toHaveTitle(/Playwright/);
});
```

## Run tests

```bash
npx playwright test
npx playwright test --headed
npx playwright test --ui
npx playwright test --project=chromium
npx playwright test tests/login.spec.ts
```

## Config

`playwright.config.ts` sets baseURL, browsers, retries, reporters, and timeouts.

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
});
```
