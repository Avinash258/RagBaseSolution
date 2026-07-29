# Web learned: what is playwright mcp

Original question: what is playwright mcp
Engine: playwright_docs
Google: https://www.google.com/search?q=playwright+what+is+playwright+mcp&hl=en

## Playwrightlearning
Source: https://avinash258.github.io/PlaywrightLearning/

URL Source: https://avinash258.github.io/PlaywrightLearning/

Published Time: Tue, 28 Jul 2026 05:47:58 GMT

Markdown Content:
## Search results

## Playwright with TypeScript — complete study material

Everything you need to go from zero to writing production-grade end-to-end tests: locators, auto-waiting, fixtures, Page Object Model, API testing, network mocking, CI pipelines, plus a cheat sheet, 30 interview questions and a scored quiz.

@playwright/test TypeScript Chromium · Firefox · WebKit Parallel by default Auto-wait Trace viewer

## What is Playwright?

Playwright is an open-source automation framework from Microsoft for end-to-end testing of modern web apps. One API drives Chromium, Firefox and WebKit, on Windows/macOS/Linux, headless or headed.

### Core mental model

Think in three layers. A **Browser** is the expensive process you launch once. A **BrowserContext** is a cheap isolated profile (cookies, storage, cache) — like a fresh incognito window. A **Page** is a tab inside that context. Every test gets its own context by default, which is why Playwright can run in parallel without tests leaking cookies or localStorage into each other.

Commands travel over a persistent WebSocket using browser developer-protocol style APIs (not classic WebDriver HTTP). That lets Playwright batch work, intercept network traffic, and inspect the DOM deeply — the foundation for auto-waiting, tracing, and mocking.

### 🚀 Fast & parallel

Tests run in parallel worker processes, each with an isolated browser context — like a fresh incognito profile per test.

### ⏳ Auto-waiting

Every action waits for the element to be attached, visible, stable, enabled and able to receive events. No manual sleeps.

### 🔍 Web-first assertions

`expect()` retries until the condition passes or the timeout expires — kills flakiness caused by async UIs.

### 🧰 Tooling

Codegen recorder, UI Mode, Trace Viewer with DOM snapshots, HTML reporter, VS Code extension.

### 🌐 Full stack

UI + API testing in the same suite, network interception, mobile emulation, geolocation, permissions, downloads.

### 🧩 TypeScript-native

Ships with types; the runner transpiles TS out of the box — no Babel/ts-node wiring needed.

## Playwright vs Cypress vs Selenium

| Aspect | Playwright | Cypress | Selenium |
| --- | --- | --- | --- |
| Architecture | WebSocket to browser (out-of-process) | Runs inside the browser | WebDriver / BiDi protocol |
| Browsers | Chromium, Firefox, WebKit | Chromium family, Firefox, WebKit (exp.) | All major browsers |
| Languages | TS/JS, Python, Java, .NET | JS/TS only | Many |
| Parallelism | Built-in, free | Paid dashboard / plugins | Grid setup required |
| Auto-wait | Yes, built-in | Yes | Manual explicit waits |
| Multi-tab / multi-origin | Native | Limited | Supported |
| Trace / time travel | Trace Viewer | Time travel snapshots | Third-party |

### When to choose Playwright

Choose it when you need reliable cross-browser E2E, multi-tab or multi-origin flows, API + UI in one suite, or strong CI tooling (traces, sharding, Docker images). Prefer lower layers of the test pyramid for pure business logic; use Playwright for journeys a real user would notice breaking — login, search, checkout, permissions, critical dashboards.

**How to use this site:** work top-to-bottom through the sidebar, copy each snippet into a real project, then finish with the Cheat sheet, Interview Q&A and the Quiz. Every code block has a **Copy** button. Press / to search.

## Le

## Intro
Source: https://playwright.dev/docs/intro

URL Source: https://playwright.dev/docs/intro

Markdown Content:
## Introduction[​](https://playwright.dev/docs/intro#introduction "Direct link to Introduction")

Playwright Test is an end-to-end test framework for modern web apps. It bundles test runner, assertions, isolation, parallelization and rich tooling. Playwright supports Chromium, WebKit and Firefox on Windows, Linux and macOS, locally or in CI, headless or headed, with native mobile emulation for Chrome (Android) and Mobile Safari.

**You will learn**

*   [How to install Playwright](https://playwright.dev/docs/intro#installing-playwright)
*   [What's installed](https://playwright.dev/docs/intro#whats-installed)
*   [How to run the example test](https://playwright.dev/docs/intro#running-the-example-test)
*   [How to open the HTML test report](https://playwright.dev/docs/intro#html-test-reports)

## Installing Playwright[​](https://playwright.dev/docs/intro#installing-playwright "Direct link to Installing Playwright")

Get started by installing Playwright using one of the following methods.

### Using npm, yarn or pnpm[​](https://playwright.dev/docs/intro#using-npm-yarn-or-pnpm "Direct link to Using npm, yarn or pnpm")

The command below either initializes a new project or adds Playwright to an existing one.

*   npm
*   yarn
*   pnpm

`npm init playwright@latest`

When prompted, choose / confirm:

*   TypeScript or JavaScript (default: TypeScript)
*   Tests folder name (default: `tests`, or `e2e` if `tests` already exists)
*   Add a GitHub Actions workflow (recommended for CI)
*   Install Playwright browsers (default: yes)

You can re-run the command later; it does not overwrite existing tests.

### Using the VS Code Extension[​](https://playwright.dev/docs/intro#using-the-vs-code-extension "Direct link to Using the VS Code Extension")

You can also create and run tests with the [VS Code Extension](https://playwright.dev/docs/getting-started-vscode).

## What's Installed[​](https://playwright.dev/docs/intro#whats-installed "Direct link to What's Installed")

Playwright downloads required browser binaries and creates the scaffold below.

`playwright.config.ts         # Test configurationpackage.jsonpackage-lock.json            # Or yarn.lock / pnpm-lock.yamltests/  example.spec.ts            # Minimal example test`

The [playwright.config](https://playwright.dev/docs/test-configuration) centralizes configuration: target browsers, timeouts, retries, projects, reporters and more. In existing projects dependencies are added to your current `package.json`.

`tests/` contains a minimal starter test.

## Running the Example Test[​](https://playwright.dev/docs/intro#running-the-example-test "Direct link to Running the Example Test")

By default tests run headless in parallel across Chromium, Firefox and WebKit (configurable in [playwright.config](https://playwright.dev/docs/test-configuration)). Output and aggregated results display in the terminal.

*   npm
*   yarn
*   pnpm

`npx playwright test`

![Image 1: tests running in command line](https://playwright.dev/assets/images/run-tests-cli-6e7e3119a14239c9021b406d7109dc44.png)

Tips:

*   See the browser window: add `--headed`.
*   Run a single project/browser: `--project=chromium`.
*   Run one file: `npx playwright test tests/example.spec.ts`.
*   Open testing UI: `--ui`.

See [Running Tests](https://playwright.dev/docs/running-tests) for details on filtering, headed mode, sharding and retries.

## HTML Test Reports[​](https://play
