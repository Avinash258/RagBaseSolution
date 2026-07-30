# Web learned: How do I screenshot a full page in Playwright?

Original question: How do I screenshot a full page in Playwright?
Engine: playwright_docs
Google: https://www.google.com/search?q=playwright+How+do+I+screenshot+a+full+page+in+Playwright%3F&hl=en

## Pages
Source: https://playwright.dev/docs/pages

URL Source: https://playwright.dev/docs/pages

Markdown Content:
## Pages[​](https://playwright.dev/docs/pages#pages "Direct link to Pages")

Each [BrowserContext](https://playwright.dev/docs/api/class-browsercontext "BrowserContext") can have multiple pages. A [Page](https://playwright.dev/docs/api/class-page "Page") refers to a single tab or a popup window within a browser context. It should be used to navigate to URLs and interact with the page content.

`// Create a page.const page = await context.newPage();// Navigate explicitly, similar to entering a URL in the browser.await page.goto('http://example.com');// Fill an input.await page.locator('#search').fill('query');// Navigate implicitly by clicking a link.await page.locator('#submit').click();// Expect a new url.console.log(page.url());`

## Multiple pages[​](https://playwright.dev/docs/pages#multiple-pages "Direct link to Multiple pages")

Each browser context can host multiple pages (tabs).

*   Each page behaves like a focused, active page. Bringing the page to front is not required.
*   Pages inside a context respect context-level emulation, like viewport sizes, custom network routes or browser locale.

`// Create two pagesconst pageOne = await context.newPage();const pageTwo = await context.newPage();// Get pages of a browser contextconst allPages = context.pages();`

## Handling new pages[​](https://playwright.dev/docs/pages#handling-new-pages "Direct link to Handling new pages")

The `page` event on browser contexts can be used to get new pages that are created in the context. This can be used to handle new pages opened by `target="_blank"` links.

`// Start waiting for new page before clicking. Note no await.const pagePromise = context.waitForEvent('page');await page.getByText('open new tab').click();const newPage = await pagePromise;// Interact with the new page normally.await newPage.getByRole('button').click();console.log(await newPage.title());`

If the action that triggers the new page is unknown, the following pattern can be used.

`// Get all new pages (including popups) in the contextcontext.on('page', async page => {  await page.waitForLoadState();  console.log(await page.title());});`

## Handling popups[​](https://playwright.dev/docs/pages#handling-popups "Direct link to Handling popups")

If the page opens a pop-up (e.g. pages opened by `target="_blank"` links), you can get a reference to it by listening to the `popup` event on the page.

This event is emitted in addition to the `browserContext.on('page')` event, but only for popups relevant to this page.

`// Start waiting for popup before clicking. Note no await.const popupPromise = page.waitForEvent('popup');await page.getByText('open the popup').click();const popup = await popupPromise;// Interact with the new popup normally.await popup.getByRole('button').click();console.log(await popup.title());`

If the action that triggers the popup is unknown, the following pattern can be used.

`// Get all popups when they openpage.on('popup', async popup => {  await popup.waitForLoadState();  console.log(await popup.title());});`

## Screenshots
Source: https://playwright.dev/docs/screenshots

URL Source: https://playwright.dev/docs/screenshots

Markdown Content:
[Skip to main content](https://playwright.dev/docs/screenshots#__docusaurus_skipToContent_fallback)

[![Image 1: Playwright logo](https://playwright.dev/img/playwright-logo.svg) **Playwright**](https://playwright.dev/)[Docs](https://playwright.dev/docs/intro)[MCP](https://playwright.dev/mcp/introduction)[CLI](https://playwright.dev/agent-cli/introduction)[API](https://playwright.dev/docs/api/class-playwright)

[Node.js](https://playwright.dev/docs/screenshots#)
*   [Node.js](https://playwright.dev/docs/screenshots)
*   [Python](https://playwright.dev/python/docs/screenshots)
*   [Java](https://playwright.dev/java/docs/screenshots)
*   [.NET](https://playwright.dev/dotnet/docs/screenshots)

[](https://github.com/microsoft/playwright)[](https://aka.ms/playwright/discord)

Search Ctrl K

*   [Getting Started](https://playwright.dev/docs/screenshots#) 
    *   [Installation](https://playwright.dev/docs/intro)
    *   [Writing tests](https://playwright.dev/docs/writing-tests)
    *   [Generating tests](https://playwright.dev/docs/codegen-intro)
    *   [Running and debugging tests](https://playwright.dev/docs/running-tests)
    *   [Trace viewer](https://playwright.dev/docs/trace-viewer-intro)
    *   [Setting up CI](https://playwright.dev/docs/ci-intro)
    *   [VS Code](https://playwright.dev/docs/getting-started-vscode)

*   [Release notes](https://playwright.dev/docs/release-notes)
*   [Canary releases](https://playwright.dev/docs/canary-releases)
*   [Playwright Test](https://playwright.dev/docs/screenshots#) 
    *   [Agents](https://playwright.dev/docs/test-agents)
    *   [Annotations](https://playwright.dev/docs/test-annotations)
    *   [Command line](https://playwright.dev/docs/test-cli)
    *   [Configuration](https://playwright.dev/docs/test-configuration)
    *   [Configuration (use)](https://playwright.dev/docs/test-use-options)
    *   [Emulation](https://playwright.dev/docs/emulation)
    *   [Fixtures](https://playwright.dev/docs/test-fixtures)
    *   [Global setup and teardown](https://playwright.dev/docs/test-global-setup-teardown)
    *   [Parallelism](https://playwright.dev/docs/test-parallel)
    *   [Parameterize tests](https://playwright.dev/docs/test-parameterize)
    *   [Projects](https://playwright.dev/docs/test-projects)
    *   [Reporters](https://playwright.dev/docs/test-reporters)
    *   [Retries](https://playwright.dev/docs/test-retries)
    *   [Sharding](https://playwright.dev/docs/test-sharding)
    *   [Timeouts](https://playwright.dev/docs/test-timeouts)
    *   [TypeScript](https://playwright.dev/docs/test-typescript)
    *   [UI Mode](https://playwright.dev/docs/test-ui-mode)
    *   [Web server](https://playwright.dev/docs/test-webserver)

*   [Guides](https://playwright.dev/docs/screenshots#) 
    *   [Library](https://playwright.dev/docs/library)
    *   [Accessibility testing](https://playwright.dev/docs/accessibility-testing)
    *   [Actions](https://playwright.dev/docs/input)
    *   [Assertions](https://playwright.dev/docs/test-assertions)
    *   [API testing](https://playwright.dev/docs/api-testing)
    *   [Authentication](https://playwright.dev/docs/auth)
    *   [Auto-waiting](https://playwright.dev/docs/actionability)
    *   [Best Practices](https://playwright.dev/docs/best-practices)
    *   [Browsers](https://playwright.dev/docs/browsers)
    *   [Chrome extensions](https://playwright.dev/docs/chrome-extensions)


## Playwrightlearning
Source: https://avinash258.github.io/PlaywrightLearning/

URL Source: https://avinash258.github.io/PlaywrightLearning/

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

## Learning roadmap

A realistic ~4 week path, assum
