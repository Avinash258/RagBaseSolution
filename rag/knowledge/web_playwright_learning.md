# Playwright + TypeScript Study Material

Source: https://avinash258.github.io/PlaywrightLearning/

☰ 

🎭 Playwright + TypeScriptStudy material & reference 

🌙 

#### Getting started

Overview Learning roadmap Install & project setup Your first test TypeScript essentials 

#### Core API

Locators Actions Assertions Auto-waiting & timeouts Frames, tabs, dialogs 

#### Structure

Hooks & test organisation Fixtures playwright.config.ts Page Object Model Data-driven testing 

#### Advanced

Authentication & state API testing Network mocking Visual & a11y testing Debugging & reports Sharding CI/CD & Docker Best practices 

#### Practice

Cheat sheet Interview Q&A Quiz (20 Q) Resources 

## Search results

# Playwright with TypeScript — complete study material

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

| Aspect                   | Playwright                            | Cypress                                 | Selenium                  |
| ------------------------ | ------------------------------------- | --------------------------------------- | ------------------------- |
| Architecture             | WebSocket to browser (out-of-process) | Runs inside the browser                 | WebDriver / BiDi protocol |
| Browsers                 | Chromium, Firefox, WebKit             | Chromium family, Firefox, WebKit (exp.) | All major browsers        |
| Languages                | TS/JS, Python, Java, .NET             | JS/TS only                              | Many                      |
| Parallelism              | Built-in, free                        | Paid dashboard / plugins                | Grid setup required       |
| Auto-wait                | Yes, built-in                         | Yes                                     | Manual explicit waits     |
| Multi-tab / multi-origin | Native                                | Limited                                 | Supported                 |
| Trace / time travel      | Trace Viewer                          | Time travel snapshots                   | Third-party               |

### When to choose Playwright

Choose it when you need reliable cross-browser E2E, multi-tab or multi-origin flows, API + UI in one suite, or strong CI tooling (traces, sharding, Docker images). Prefer lower layers of the test pyramid for pure business logic; use Playwright for journeys a real user would notice breaking — login, search, checkout, permissions, critical dashboards.

**How to use this site:** work top-to-bottom through the sidebar, copy each snippet into a real project, then finish with the Cheat sheet, Interview Q&A and the Quiz. Every code block has a **Copy** button. Press / to search.

## Learning roadmap

A realistic \~4 week path, assuming 1–2 hours per day.

### Theory: skill layers

Learn Playwright in layers, not as a pile of APIs. First master **finding and waiting** (locators + auto-wait) — that alone removes most beginner flakes. Next learn **expressing intent** (assertions, hooks, config). Then learn **scaling a suite** (fixtures, POM, auth, data). Finally learn **operating in CI** (traces, sharding, Docker). Skipping ahead to Page Objects before you understand locators usually produces brittle wrappers around brittle selectors.

1. **Week 1 — Foundations.** Node + npm, TypeScript basics (types, interfaces, async/await, modules), install Playwright, run the sample tests, learn the CLI flags.
2. **Week 1 — Locators.** Master `getByRole`, `getByLabel`, `getByTestId`, filtering, chaining, and strictness.
3. **Week 2 — Actions & assertions.** click/fill/select/upload, web-first assertions, soft assertions, auto-waiting model and timeouts.
4. **Week 2 — Structure.** Hooks, describe blocks, tags, annotations, `playwright.config.ts`, projects, reporters.
5. **Week 3 — Design patterns.** Page Object Model, custom fixtures, component helpers, data-driven tests, faker data.
6. **Week 3 — Advanced.** Storage state auth, API testing with `request`, route mocking, downloads/uploads, iframes, visual snapshots.
7. **Week 4 — Quality & delivery.** Trace Viewer, retries, sharding, GitHub Actions, Docker, reporting, flake triage.
8. **Week 4 — Build a portfolio suite.** 20–30 tests against a real demo app, POM + fixtures + CI badge + HTML report published.

**Practice targets:** TodoMVC demo, SauceDemo, ExpandTesting, ReqRes (API).

## Install & project setup

Requirements: Node.js 18+ (20 LTS recommended), npm, and VS Code with the official _Playwright Test for VSCode_ extension.

### What gets installed

`@playwright/test` is both the test runner and the browser automation library. Separately, `npx playwright install` downloads browser binaries (Chromium, Firefox, WebKit) into a local cache — they are not the browsers already on your machine. That isolation is intentional: CI and laptops run the same browser builds, so “works on my Chrome” drift is rare.

**Theory tip:** workers (parallel processes) share one installed browser binary but each opens its own BrowserContext. Parallelism scales with CPU; flakiness usually comes from shared test data, not from workers themselves.

### 1\. Scaffold a new project

```
# interactive installer — choose TypeScript, tests folder, GH Actions, install browsers
npm init playwright@latest

# or non-interactive
npm init playwright@latest -- --lang=ts --quiet
```

### 2\. Add to an existing project

```
npm i -D @playwright/test typescript @types/node
npx playwright install --with-deps          # browsers + OS libs
npx playwright install chromium             # single browser only
```

### 3\. Generated structure

```
my-app/
├─ tests/                  # your specs
│  └─ example.spec.ts
├─ tests-examples/         # demo specs (safe to delete)
├─ playwright.config.ts    # main configuration
├─ package.json
├─ tsconfig.json
├─ playwright-report/      # HTML report output  (gitignore)
└─ test-results/           # traces, videos, screenshots (gitignore)
```

### 4\. Useful npm scripts

```
{
  "scripts": {
    "test": "playwright test",
    "test:headed": "playwright test --headed",
    "test:ui": "playwright test --ui",
    "test:chrome": "playwright test --project=chromium",
    "test:debug": "playwright test --debug",
    "report": "playwright show-report",
    "codegen": "playwright codegen https://demo.playwright.dev/todomvc"
  }
}
```

### 5\. CLI you will actually use

| Command                                  | What it does                               |
| ---------------------------------------- | ------------------------------------------ |
| npx playwright test                      | Run all tests, headless, all projects      |
| npx playwright test login.spec.ts        | Run one file                               |
| npx playwright test -g "adds a todo"     | Run tests whose title matches              |
| npx playwright test --ui                 | UI Mode: watch, time-travel, pick locators |
| npx playwright test --debug              | Inspector, step-by-step                    |
| npx playwright test --headed --workers=1 | Watch it run in a real window, serially    |
| npx playwright test --repeat-each=5      | Flake hunting                              |
| npx playwright test --last-failed        | Re-run only previous failures              |
| npx playwright test --shard=1/3          | Split across CI machines                   |
| npx playwright codegen URL               | Record actions into TS code                |
| npx playwright show-trace trace.zip      | Open Trace Viewer                          |
| npx playwright install --with-deps       | Download browsers & deps                   |

### 6\. tsconfig.json that plays nicely

```
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "types": ["node"],
    "baseUrl": ".",
    "paths": { "@pages/*": ["pages/*"], "@fixtures/*": ["fixtures/*"] }
  },
  "include": ["tests", "pages", "fixtures", "playwright.config.ts"]
}
```

Playwright transpiles TypeScript itself (via esbuild) and **does not type-check** at run time. Add `"typecheck": "tsc --noEmit"` to your scripts and run it in CI.

## Your first test

A Playwright test is a small story: arrange the page, act like a user, assert what the user should see. The runner supplies a fresh `page` fixture so you do not manage browser lifecycle yourself.

### Mental model

* **Arrange** — navigate or seed state (`beforeEach`, API setup, storage state).
* **Act** — interact through locators (`fill`, `click`, `press`).
* **Assert** — use web-first `expect(locator)` so Playwright retries until the UI settles.
* **Isolation** — do not rely on another test having run first; each test should leave (or recreate) the world it needs.

```
// tests/todo.spec.ts
import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('https://demo.playwright.dev/todomvc');
});

test('should add a todo item', async ({ page }) => {
  const newTodo = page.getByPlaceholder('What needs to be done?');

  await newTodo.fill('Learn Playwright');
  await newTodo.press('Enter');

  await expect(page.getByTestId('todo-title')).toHaveText('Learn Playwright');
  await expect(page.getByTestId('todo-item')).toHaveCount(1);
});

test('should mark a todo as completed', async ({ page }) => {
  const input = page.getByPlaceholder('What needs to be done?');
  await input.fill('Write tests');
  await input.press('Enter');

  await page.getByRole('checkbox', { name: 'Toggle Todo' }).check();
  await expect(page.getByTestId('todo-item')).toHaveClass(/completed/);
});
```

### Anatomy

* `test(title, fn)` — declares a test; the callback receives _fixtures_ by destructuring.
* `{ page }` — a built-in fixture: a brand-new page in a fresh isolated browser context.
* `await` — **every** Playwright call is async. A missing `await` is the #1 source of flaky tests.
* `expect(locator)` — web-first assertion, auto-retries until timeout.

### Run it

```
npx playwright test tests/todo.spec.ts --headed --project=chromium
npx playwright show-report
```

**Async gotcha**  
`page.click('#save')` without `await` returns a floating Promise — the test may finish before the click resolves. Enable ESLint rule `@typescript-eslint/no-floating-promises`.

## TypeScript essentials for Playwright

You don't need advanced TS. These are the pieces that show up in real test code.

### Why TypeScript in test automation?

* **Catch mistakes early.** Wrong fixture names, mistyped locator options, and bad API payload shapes fail in the editor — not after a 20-minute CI run.
* **Document contracts.** `interface User` and page-object method signatures become living docs for the team.
* **Safe reuse.** Fixtures, factories and helpers stay composable because their inputs/outputs are named and checked.
* **Runtime note:** Playwright transpiles with esbuild and does _not_ type-check. Keep `tsc --noEmit` in CI so types stay honest.

### Types you'll import

```
import { test, expect, type Page, type Locator, type BrowserContext,
         type APIRequestContext, type TestInfo } from '@playwright/test';

class LoginPage {
  readonly page: Page;
  readonly username: Locator;

  constructor(page: Page) {
    this.page = page;
    this.username = page.getByLabel('Username');
  }
}
```

### Interfaces & type aliases for test data

```
export interface User {
  username: string;
  password: string;
  role: 'admin' | 'editor' | 'viewer';   // union type
  meta?: Record<string, unknown>;        // optional
}

export const users: readonly User[] = [
  { username: 'std_user',  password: 'secret', role: 'viewer' },
  { username: 'admin_user', password: 'secret', role: 'admin' },
] as const;
```

### async / await and Promise handling

```
// sequential
const title: string = await page.title();
const count: number = await page.getByRole('listitem').count();

// parallel — both start at once
const [response] = await Promise.all([
  page.waitForResponse(r => r.url().includes('/api/cart') && r.status() === 200),
  page.getByRole('button', { name: 'Add to cart' }).click(),
]);

// typed JSON body
type Cart = { items: { sku: string; qty: number }[]; total: number };
const cart = (await response.json()) as Cart;
```

### Generics & utility types you'll meet

| Type                  | Use                                                |
| --------------------- | -------------------------------------------------- |
| Partial<User>         | Builder / override patterns in test data factories |
| Pick<User,'username'> | Narrow a fixture's payload                         |
| Record<string,string> | Headers, query params, env maps                    |
| keyof typeof obj      | Typed keys of a config object                      |
| as const              | Freeze literal test data into narrow types         |

### Env variables, typed

```
// env.ts
import 'dotenv/config';

function required(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`Missing env var: ${name}`);
  return v;
}

export const ENV = {
  baseURL: process.env.BASE_URL ?? 'https://staging.example.com',
  user: required('APP_USER'),
  pass: required('APP_PASS'),
} as const;
```

## Locators — the heart of Playwright

A `Locator` is a _lazy_, re-resolving description of how to find an element. It is not a handle to a DOM node — it re-queries the DOM every time you use it, which is why Playwright survives re-renders.

### Theory: why locator strategy matters

* **Resilience.** Role/label/text locators mirror how users and screen readers identify controls. When a designer renames a CSS class, those tests keep working.
* **Accessibility tree.** `getByRole` reads the browser accessibility tree (roles, names, states). If a control is hard to locate by role, real users with assistive tech often struggle too — so good locators push better UI.
* **Lazy evaluation.** Creating a locator does nothing to the page. Only an action or assertion triggers lookup + auto-wait. You can declare locators in page objects safely at construction time.
* **Strict mode.** Ambiguous matches fail loudly. That is deliberate: silent “click the first match” hides bugs and flakes.

### Recommended, in priority order

```
// 1. Role — mirrors how assistive tech sees the page (most resilient)
page.getByRole('button', { name: 'Sign in' });
page.getByRole('link',   { name: /docs/i });
page.getByRole('textbox',{ name: 'Email' });
page.getByRole('heading',{ level: 2, name: 'Checkout' });
page.getByRole('checkbox', { checked: true });

// 2. Label / placeholder — form fields
page.getByLabel('Password');
page.getByPlaceholder('Search products');

// 3. Text — non-interactive content
page.getByText('Order confirmed');            // substring, case-insensitive-ish
page.getByText('Order confirmed', { exact: true });

// 4. Alt text / title
page.getByAltText('Company logo');
page.getByTitle('Close dialog');

// 5. Test id — your escape hatch, stable by contract
page.getByTestId('checkout-submit');

// 6. CSS / XPath — last resort
page.locator('.price > span');
page.locator('//div[@id="total"]');
```

**Rule of thumb:** user-facing locators first (role/label/text), `data-testid` when the UI has no accessible handle, CSS/XPath only when nothing else works.

### Custom test-id attribute

```
// playwright.config.ts
export default defineConfig({
  use: { testIdAttribute: 'data-qa' },   // now getByTestId('x') → [data-qa="x"]
});
```

### Chaining, filtering, narrowing

```
const row = page.getByRole('row').filter({ hasText: 'MacBook Pro' });
await row.getByRole('button', { name: 'Delete' }).click();

// filter by a child locator
page.getByRole('listitem').filter({ has: page.getByText('Out of stock') });

// exclude
page.getByRole('listitem').filter({ hasNotText: 'Archived' });

// scope to a container
const dialog = page.getByRole('dialog');
await dialog.getByLabel('Reason').fill('Damaged');
await dialog.getByRole('button', { name: 'Confirm' }).click();

// positional
page.getByRole('listitem').first();
page.getByRole('listitem').last();
page.getByRole('listitem').nth(2);

// logical operators
page.getByRole('button').and(page.getByTitle('Submit'));
page.getByRole('button', { name: 'New' }).or(page.getByRole('button', { name: 'Create' }));
```

### Strictness

If a locator matches more than one element, actions throw `strict mode violation`. Fix it by narrowing (`.filter()`, scoping, `.first()`) — never by disabling strictness.

### Working with lists

```
const items = page.getByRole('listitem');

await expect(items).toHaveCount(5);
const texts: string[] = await items.allTextContents();
await expect(items).toHaveText(['A', 'B', 'C']);   // exact order

for (const item of await items.all()) {
  console.log(await item.textContent());
}
```

### Locator vs ElementHandle

| Locator ✅      | ElementHandle ⚠️ (legacy)    |                         |
| -------------- | ---------------------------- | ----------------------- |
| Resolution     | Lazy, re-queried on each use | Bound to one DOM node   |
| Auto-wait      | Yes                          | Partial                 |
| Stale elements | Immune                       | Breaks after re-render  |
| Use when       | Always                       | Rare low-level DOM work |

## Actions

Actions are how your test behaves like a user: click, type, select, upload, navigate. Playwright does not fire a raw DOM event and move on — it waits until the target is actionable, then performs a realistic interaction.

### Theory: actionability before action

* **User realism.** `click()` scrolls into view, checks the hit target, then clicks the centre (or a point you choose). Overlays and disabled buttons surface as timeouts instead of false greens.
* **`fill` vs `pressSequentially`.** `fill` sets the value quickly (great for most forms). Use key-by-key typing when the app listens to individual `keydown` events (autocomplete, OTP inputs).
* **Force is a smell.** `{ force: true }` skips actionability. Prefer fixing the locator or waiting for the real UI state; force hides product bugs.
* **Events first.** For downloads, popups and file choosers, register `waitForEvent` _before_ the click that triggers them, or you race the event.

### Mouse & keyboard

```
await locator.click();
await locator.click({ button: 'right' });
await locator.click({ clickCount: 2 });       // or locator.dblclick()
await locator.click({ modifiers: ['Control'] });
await locator.click({ position: { x: 5, y: 5 } });
await locator.click({ force: true });         // skip actionability — use sparingly
await locator.hover();
await locator.focus();
await locator.blur();

await locator.fill('hello');                  // clears then sets value (fast)
await locator.clear();
await locator.pressSequentially('h-e-l-l-o', { delay: 100 }); // real keystrokes
await locator.press('Enter');
await page.keyboard.press('Control+A');
await page.mouse.wheel(0, 600);
```

### Checkboxes, radios, selects

```
await page.getByLabel('Subscribe').check();
await page.getByLabel('Subscribe').uncheck();
await page.getByLabel('Subscribe').setChecked(true);

await page.getByLabel('Country').selectOption('IN');
await page.getByLabel('Country').selectOption({ label: 'India' });
await page.getByLabel('Tags').selectOption(['a', 'b']);   // multi-select
```

### Files

```
// upload
await page.getByLabel('Upload').setInputFiles('tests/data/invoice.pdf');
await page.getByLabel('Upload').setInputFiles([]);        // clear
await page.getByLabel('Upload').setInputFiles({
  name: 'note.txt', mimeType: 'text/plain', buffer: Buffer.from('hi'),
});

// hidden input behind a styled button
const chooser = page.waitForEvent('filechooser');
await page.getByRole('button', { name: 'Choose file' }).click();
await (await chooser).setFiles('tests/data/logo.png');

// download
const downloadPromise = page.waitForEvent('download');
await page.getByRole('link', { name: 'Export CSV' }).click();
const download = await downloadPromise;
await download.saveAs('./downloads/' + download.suggestedFilename());
```

### Drag & drop, scrolling

```
await page.getByTestId('card-1').dragTo(page.getByTestId('column-done'));

// manual, for finicky HTML5 DnD
await source.hover();
await page.mouse.down();
await target.hover();
await page.mouse.up();

await locator.scrollIntoViewIfNeeded();
```

### Navigation

```
await page.goto('/checkout');                 // relative to baseURL
await page.goBack();
await page.goForward();
await page.reload();
await page.waitForURL('**/dashboard');
```

### Reading state

```
const text  = await locator.textContent();
const inner = await locator.innerText();
const value = await locator.inputValue();
const href  = await locator.getAttribute('href');
const n     = await locator.count();
const vis   = await locator.isVisible();
const on    = await locator.isEnabled();

// run JS in the page
const scrollY = await page.evaluate(() => window.scrollY);
await locator.evaluate((el: HTMLElement) => el.style.border = '2px solid red');
```

## Assertions

**Web-first assertions** take a Locator/Page and retry until they pass or `expect.timeout` (default 5 s) expires.

### Theory: retry vs snapshot-in-time

* **Web-first** (`expect(locator).toHaveText(...)`) re-queries the DOM on every attempt. Perfect for SPAs where content arrives asynchronously.
* **Value assertions** (`expect(total).toBe(42)`) check a number/string you already hold. They do _not_ retry — if you read too early, you flake.
* **Soft assertions** collect failures and continue, useful for multi-field form validation in one test. Hard assertions stop at the first failure.
* **Prefer outcomes over steps.** Assert “Order confirmed” is visible, not that three intermediate spinners appeared.

### Locator assertions

```
await expect(loc).toBeVisible();
await expect(loc).toBeHidden();
await expect(loc).toBeAttached();
await expect(loc).toBeEnabled();
await expect(loc).toBeDisabled();
await expect(loc).toBeEditable();
await expect(loc).toBeEmpty();
await expect(loc).toBeChecked();
await expect(loc).toBeFocused();
await expect(loc).toBeInViewport();

await expect(loc).toHaveText('Exact text');
await expect(loc).toHaveText(/partial/i);
await expect(loc).toContainText('sub');
await expect(loc).toHaveValue('abc');
await expect(loc).toHaveValues(['a', 'b']);
await expect(loc).toHaveAttribute('href', '/home');
await expect(loc).toHaveClass(/active/);
await expect(loc).toHaveCount(3);
await expect(loc).toHaveCSS('color', 'rgb(255, 0, 0)');
await expect(loc).toHaveId('main');
await expect(loc).toHaveJSProperty('checked', true);
await expect(loc).toHaveAccessibleName('Close');
await expect(loc).toHaveScreenshot('card.png');
```

### Page & response assertions

```
await expect(page).toHaveTitle(/Dashboard/);
await expect(page).toHaveURL(/\/orders\/\d+/);
await expect(page).toHaveScreenshot('home.png', { fullPage: true });
await expect(apiResponse).toBeOK();
```

### Non-retrying (plain value) assertions

```
expect(total).toBe(42);
expect(list).toHaveLength(3);
expect(obj).toEqual({ id: 1, name: 'A' });
expect(obj).toMatchObject({ name: 'A' });
expect(str).toContain('ok');
expect(arr).toContainEqual({ id: 1 });
expect(fn).toThrow();
expect(value).toBeTruthy();
expect(value).not.toBeNull();
```

### Soft assertions & custom messages

```
await expect.soft(page.getByTestId('sku')).toHaveText('AB-1');
await expect.soft(page.getByTestId('price')).toHaveText('₹999');
// test continues, then fails at the end with all soft failures reported

await expect(loc, 'Submit must be enabled after filling the form').toBeEnabled();
```

### Polling & custom timeouts

```
await expect(loc).toBeVisible({ timeout: 15_000 });

// poll any async value
await expect.poll(async () => (await api.get('/status')).status(), {
  message: 'service should become healthy',
  timeout: 30_000,
  intervals: [500, 1000, 2000],
}).toBe(200);

// retry a whole block
await expect(async () => {
  const res = await api.get('/jobs/1');
  expect((await res.json()).state).toBe('done');
}).toPass({ timeout: 60_000 });
```

### Custom matcher

```
import { expect as baseExpect } from '@playwright/test';

export const expect = baseExpect.extend({
  async toHaveErrorMessage(locator, expected: string) {
    const actual = await locator.getAttribute('data-error');
    return {
      pass: actual === expected,
      message: () => `expected data-error "${expected}", got "${actual}"`,
    };
  },
});
```

## Auto-waiting & timeouts

Before any action, Playwright runs **actionability checks** and retries until they all pass.

### Theory: time is a budget, not a sleep

Flaky suites almost always misuse time: hard sleeps that are too short on a slow CI agent, or too long locally. Playwright’s model is different — keep retrying a _condition_ until the budget (timeout) is spent. You configure budgets at several levels; the tightest relevant timeout wins for that operation, capped by the test timeout.

| Check           | Meaning                                         | Applies to          |
| --------------- | ----------------------------------------------- | ------------------- |
| Attached        | Element is in the DOM                           | all                 |
| Visible         | Non-empty box, not visibility:hidden            | click, fill, hover… |
| Stable          | Same bounding box for 2 animation frames        | click, hover, drag  |
| Enabled         | Not disabled                                    | click, fill, select |
| Editable        | Not readonly                                    | fill, clear         |
| Receives events | Hit-target test passes (not covered by overlay) | click, tap          |

### Timeout hierarchy

| Timeout            | Default                      | Set where                             |
| ------------------ | ---------------------------- | ------------------------------------- |
| Test timeout       | 30 s                         | timeout in config · test.setTimeout() |
| Expect timeout     | 5 s                          | expect.timeout · per assertion        |
| Action timeout     | 0 (no limit, capped by test) | use.actionTimeout                     |
| Navigation timeout | 0 (capped by test)           | use.navigationTimeout                 |
| Global timeout     | none                         | globalTimeout                         |
| Hook timeout       | 30 s                         | test.setTimeout() inside hook         |

```
test.setTimeout(120_000);
test.slow();                       // triples the timeout
await expect(loc).toBeVisible({ timeout: 20_000 });
```

### Explicit waits (when you truly need them)

```
await page.waitForURL('**/dashboard');
await page.waitForLoadState('networkidle');       // discouraged; prefer assertions
await page.waitForResponse(r => r.url().includes('/api/orders') && r.ok());
await page.waitForRequest('**/analytics**');
await page.waitForFunction(() => document.readyState === 'complete');
await page.waitForEvent('popup');
await locator.waitFor({ state: 'visible' });      // 'attached'|'detached'|'visible'|'hidden'
```

**Anti-pattern:** `await page.waitForTimeout(3000)`. Hard sleeps are slow when unnecessary and still flaky when the app is slower. Assert on the observable end-state instead.

**Better:** 

```
// ❌ await page.waitForTimeout(3000);
// ✅
await expect(page.getByRole('alert')).toHaveText('Saved');
```

## Frames, tabs, dialogs, mobile

Real apps are rarely a single document. Payments live in iframes, OAuth opens popups, confirms use native dialogs, and mobile viewports change layout. Playwright models each of these explicitly so your tests stay deterministic.

### Theory: separate browsing worlds

* **Frames** have their own document and origin. Locators on `page` do not pierce iframes — use `frameLocator` (preferred) so auto-wait still applies inside the frame.
* **Tabs/popups** are extra `Page` objects in the same context (shared cookies) or a new context if you create one. Always await `popup` before interacting.
* **Dialogs** are browser-native and block the page. Register a handler before the triggering click; otherwise Playwright auto-dismisses them.
* **Devices** are presets (viewport, user-agent, touch). Emulation is not a real phone, but it catches responsive and permission issues early.

### iframes

```
const frame = page.frameLocator('#payment-iframe');
await frame.getByLabel('Card number').fill('4111111111111111');
await frame.getByRole('button', { name: 'Pay' }).click();

// nested
page.frameLocator('#outer').frameLocator('#inner').getByText('Deep');
```

### New tabs / popups

```
const popupPromise = page.waitForEvent('popup');
await page.getByRole('link', { name: 'Open docs' }).click();
const popup = await popupPromise;
await popup.waitForLoadState();
await expect(popup).toHaveTitle(/Documentation/);
await popup.close();

// brand-new page in the same context (shares cookies/session)
const page2 = await context.newPage();
```

### Dialogs (alert / confirm / prompt)

```
page.on('dialog', async dialog => {
  expect(dialog.type()).toBe('confirm');
  expect(dialog.message()).toContain('Delete this item?');
  await dialog.accept();          // or dialog.dismiss(); prompt: accept('text')
});
await page.getByRole('button', { name: 'Delete' }).click();
```

If no `dialog` handler is registered, Playwright auto-dismisses dialogs.

### Mobile emulation, geolocation, permissions

```
import { devices } from '@playwright/test';

// in config projects
{ name: 'iPhone 14', use: { ...devices['iPhone 14'] } }

// ad hoc
const context = await browser.newContext({
  ...devices['Pixel 7'],
  locale: 'en-IN',
  timezoneId: 'Asia/Kolkata',
  geolocation: { latitude: 23.1815, longitude: 79.9864 },  // Jabalpur
  permissions: ['geolocation', 'clipboard-read'],
  colorScheme: 'dark',
});
```

### Cookies & storage

```
await context.addCookies([{ name: 'consent', value: 'yes', domain: 'example.com', path: '/' }]);
const cookies = await context.cookies();
await context.clearCookies();

await page.addInitScript(() => localStorage.setItem('tour_seen', '1'));
const token = await page.evaluate(() => localStorage.getItem('token'));
```

## Hooks & test organisation

Hooks and describe blocks structure when setup runs and how tests are grouped for reports, tags and parallel execution. Prefer thin hooks; push reusable setup into fixtures when many files need the same thing.

### Theory: lifecycle & isolation

* **beforeEach / afterEach** run around every test in the block — ideal for navigation and light cleanup.
* **beforeAll / afterAll** run once per worker for that file/describe. Do not put mutable shared UI state here unless the describe is `serial`.
* **parallel vs serial.** Default is parallel across files (and inside files if `fullyParallel`). Use serial only for true multi-step journeys that must share state.
* **Annotations** (`skip`, `fixme`, `fail`, tags) communicate intent to humans and CI filters — they are part of your suite’s documentation.

```
import { test, expect } from '@playwright/test';

test.describe('Checkout', () => {
  test.describe.configure({ mode: 'parallel' });   // or 'serial'

  test.beforeAll(async () => { /* once per worker */ });
  test.beforeEach(async ({ page }) => { await page.goto('/cart'); });
  test.afterEach(async ({ page }, testInfo) => {
    if (testInfo.status !== testInfo.expectedStatus) {
      await page.screenshot({ path: `fail-${testInfo.title}.png` });
    }
  });
  test.afterAll(async () => { /* cleanup */ });

  test('applies a coupon', async ({ page }) => { /* ... */ });
});
```

### Annotations & modifiers

```
test.skip('not implemented yet', async () => {});
test.fixme('broken on WebKit', async () => {});
test.fail('known bug PROJ-123', async () => {});
test.only('debug just this', async () => {});
test.slow();

test.skip(({ browserName }) => browserName === 'webkit', 'Safari unsupported');
test.skip(!!process.env.CI, 'Local only');

test('flaky-ish', async () => {}); // retries come from config
test.describe.serial('payment flow', () => { /* stops on first failure */ });
```

### Tags & grep

```
test('login works', { tag: ['@smoke', '@auth'] }, async ({ page }) => {});

test('slow report', {
  tag: '@regression',
  annotation: [{ type: 'issue', description: 'https://jira/PROJ-42' }],
}, async () => {});
```

```
npx playwright test --grep @smoke
npx playwright test --grep-invert @slow
npx playwright test --grep "@smoke|@auth"
```

### Steps (readable reports)

```
await test.step('Login as admin', async () => {
  await page.getByLabel('User').fill('admin');
  await page.getByLabel('Pass').fill('secret');
  await page.getByRole('button', { name: 'Sign in' }).click();
});
await test.step('Verify dashboard', async () => {
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

## Fixtures

Fixtures set up and tear down whatever a test needs, on demand. They are composable, lazily instantiated (only created if a test asks for them) and typed.

### Theory: dependency injection for tests

* **Request what you need.** Destructure fixtures in the test callback (`{ page, loginPage }`). Unused fixtures are never created — cheaper than a fat `beforeEach`.
* **Scope.** Test-scoped fixtures reset every test (isolation). Worker-scoped fixtures run once per worker (good for expensive API tokens).
* **Composition.** Fixtures can depend on other fixtures (`authedPage` uses `loginPage`). That graph replaces copy-pasted setup.
* **Auto fixtures** run for every test without being requested — use sparingly (e.g. console-error guards), because they add cost and coupling.

### Built-in fixtures

| Fixture     | Type              | Scope  | Notes                           |          |
| ----------- | ----------------- | ------ | ------------------------------- | -------- |
| page        | Page              | test   | Fresh page in a fresh context   |          |
| context     | BrowserContext    | test   | Isolated cookies/storage        |          |
| browser     | Browser           | worker | Shared across tests in a worker |          |
| browserName | string            | worker | 'chromium' \| 'firefox'         | 'webkit' |
| request     | APIRequestContext | test   | HTTP client for API tests       |          |
| baseURL     | string            | test   | From config                     |          |

### Custom fixtures (the pro pattern)

```
// fixtures/test-fixtures.ts
import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

type Pages = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  authedPage: DashboardPage;      // already logged in
};

type WorkerStuff = {
  apiToken: string;               // fetched once per worker
};

export const test = base.extend<Pages, WorkerStuff>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));                  // setup → hand over → teardown
  },

  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },

  authedPage: async ({ page, loginPage }, use) => {
    await loginPage.goto();
    await loginPage.login(process.env.APP_USER!, process.env.APP_PASS!);
    await use(new DashboardPage(page));
    // teardown after the test
    await page.context().clearCookies();
  },

  apiToken: [async ({}, use) => {
    const token = await fetchToken();
    await use(token);
  }, { scope: 'worker' }],
});

export { expect };
```

```
// tests/dashboard.spec.ts
import { test, expect } from '../fixtures/test-fixtures';

test('shows widgets after login', async ({ authedPage }) => {
  await expect(authedPage.widgets).toHaveCount(4);
});
```

### Options fixtures (configurable per project)

```
export const test = base.extend<{ tenant: string }>({
  tenant: ['acme', { option: true }],
});

// playwright.config.ts
projects: [
  { name: 'acme',  use: { tenant: 'acme'  } },
  { name: 'globex', use: { tenant: 'globex' } },
]
```

### Auto fixtures

```
export const test = base.extend<{ consoleGuard: void }>({
  consoleGuard: [async ({ page }, use) => {
    const errors: string[] = [];
    page.on('console', m => m.type() === 'error' && errors.push(m.text()));
    await use();
    expect(errors, 'no console errors').toEqual([]);
  }, { auto: true }],     // runs for every test, no need to request it
});
```

## playwright.config.ts

The config file is the control plane for your suite: where tests live, how many workers run, which browsers/projects execute, what artefacts you keep, and how the app is started. Treat it as production code — small, reviewed changes, environment-aware defaults.

### Theory: projects & environments

* **One suite, many projects.** The same specs can run as Chromium, Firefox, WebKit, or mobile without duplicating files. Projects can also mean “setup”, “admin”, “anonymous”.
* **CI vs local.** Use `process.env.CI` to tighten retries, forbid `test.only`, and avoid reusing a local web server.
* **Artefacts are a trade-off.** Traces and videos catch flakes but cost disk and time. `on-first-retry` / `retain-on-failure` are the usual sweet spot.
* **webServer.** Booting the app from config removes “did you start the server?” as a human failure mode.

```
import { defineConfig, devices } from '@playwright/test';
import 'dotenv/config';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  outputDir: './test-results',
  snapshotDir: './__snapshots__',

  timeout: 30_000,
  expect: { timeout: 5_000, toHaveScreenshot: { maxDiffPixelRatio: 0.02 } },
  globalTimeout: 30 * 60_000,

  fullyParallel: true,
  workers: process.env.CI ? 4 : undefined,     // undefined = ~half the CPU cores
  retries: process.env.CI ? 2 : 0,
  forbidOnly: !!process.env.CI,
  maxFailures: process.env.CI ? 10 : 0,

  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'results/junit.xml' }],
    ['json', { outputFile: 'results/results.json' }],
    ['blob'],                                   // for merging sharded runs
  ],

  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    headless: true,
    viewport: { width: 1440, height: 900 },
    ignoreHTTPSErrors: true,
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    trace: 'on-first-retry',      // 'on' | 'off' | 'retain-on-failure'
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    locale: 'en-IN',
    timezoneId: 'Asia/Kolkata',
    testIdAttribute: 'data-testid',
    extraHTTPHeaders: { 'x-run-id': process.env.RUN_ID ?? 'local' },
  },

  projects: [
    { name: 'setup', testMatch: /global\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: '.auth/user.json' },
      dependencies: ['setup'],
    },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit',  use: { ...devices['Desktop Safari'] } },
    { name: 'mobile',  use: { ...devices['Pixel 7'] } },
  ],

  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

### Key options explained

| Option                  | Why it matters                                                              |
| ----------------------- | --------------------------------------------------------------------------- |
| fullyParallel           | Runs tests inside a file in parallel too, not just across files             |
| retries                 | Reruns failures; a test that passes on retry is marked _flaky_              |
| trace: 'on-first-retry' | Best cost/benefit — full trace only when something failed once              |
| projects                | Same tests × browsers/devices/environments; also enables setup dependencies |
| dependencies            | Run a setup project (login, seed data) before others                        |
| webServer               | Boots your app before the suite and kills it after                          |
| forbidOnly              | Fails CI if someone committed test.only                                     |

### Global setup / teardown

```
// global.setup.ts  (as a project — the modern way)
import { test as setup, expect } from '@playwright/test';

const authFile = '.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.APP_USER!);
  await page.getByLabel('Password').fill(process.env.APP_PASS!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await page.context().storageState({ path: authFile });
});
```

## Page Object Model

Encapsulate locators and user-level actions per page/component so specs read like a user story and selector changes happen in one place.

### Theory: separation of concerns

* **Specs describe intent.** “Login fails for locked user” should not know CSS classes. Page objects hide that detail behind methods like `login()` and `expectError()`.
* **One reason to change.** When the login form markup changes, you edit `LoginPage` once — not dozens of specs.
* **Components scale better than mega-pages.** Header, cart drawer, and table widgets become reusable objects composed into pages.
* **Do not over-abstract.** Tiny one-off screens can stay inline. POM pays off when the same UI is touched by many tests.

### Base page

```
// pages/BasePage.ts
import { type Page, type Locator, expect } from '@playwright/test';

export abstract class BasePage {
  protected constructor(protected readonly page: Page, private readonly path: string) {}

  async goto(): Promise<void> {
    await this.page.goto(this.path);
  }

  async expectLoaded(heading: string): Promise<void> {
    await expect(this.page.getByRole('heading', { name: heading })).toBeVisible();
  }

  toast(text: string): Locator {
    return this.page.getByRole('alert').filter({ hasText: text });
  }
}
```

### Concrete page

```
// pages/LoginPage.ts
import { type Page, type Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
  readonly username: Locator;
  readonly password: Locator;
  readonly submit: Locator;
  readonly error: Locator;

  constructor(page: Page) {
    super(page, '/login');
    this.username = page.getByLabel('Username');
    this.password = page.getByLabel('Password');
    this.submit   = page.getByRole('button', { name: 'Sign in' });
    this.error    = page.getByTestId('login-error');
  }

  async login(user: string, pass: string): Promise<void> {
    await this.username.fill(user);
    await this.password.fill(pass);
    await this.submit.click();
  }

  async expectError(message: string | RegExp): Promise<void> {
    await expect(this.error).toHaveText(message);
  }
}
```

### Component object

```
// components/Header.ts
import { type Page, type Locator } from '@playwright/test';

export class Header {
  readonly root: Locator;
  readonly cartBadge: Locator;

  constructor(page: Page) {
    this.root = page.getByRole('banner');
    this.cartBadge = this.root.getByTestId('cart-count');
  }

  async openCart(): Promise<void> {
    await this.root.getByRole('link', { name: 'Cart' }).click();
  }
}
```

### The spec stays clean

```
import { test, expect } from '../fixtures/test-fixtures';

test.describe('Login', () => {
  test('rejects bad credentials @smoke', async ({ loginPage }) => {
    await loginPage.goto();
    await loginPage.login('bad', 'creds');
    await loginPage.expectError(/invalid username or password/i);
  });
});
```

**POM rules:** expose `Locator`s (not raw strings) · keep assertions thin or in dedicated `expectX()` methods · never put `test()` inside a page object · one class per page/component · return new page objects from navigation methods when it helps chaining.

## Data-driven testing

Data-driven tests run the same behaviour with many inputs so you cover edge cases without copying specs. Pair that with factories and API seeding so each case stays independent.

### Theory: inputs vs journeys

* **Parameterise variations, not unrelated flows.** Loop over locked/invalid users for login errors; do not stuff checkout and search into one table.
* **Unique data beats shared accounts.** Faker (or UUIDs) prevents collisions when workers run in parallel against one environment.
* **Fast setup door.** Create entities via API/DB, then assert in the UI. Clicking through five prerequisite screens multiplies flake risk.
* **Readable titles.** Include the key input in the test name (`login fails for ${user}`) so failures are greppable in CI.

### Loop over an array

```
const cases = [
  { user: 'locked_out_user', error: /locked out/i },
  { user: 'invalid_user',    error: /do not match/i },
] as const;

for (const { user, error } of cases) {
  test(`login fails for ${user}`, async ({ loginPage }) => {
    await loginPage.goto();
    await loginPage.login(user, 'secret_sauce');
    await loginPage.expectError(error);
  });
}
```

### From JSON / CSV

```
import users from '../data/users.json';               // resolveJsonModule
import { parse } from 'csv-parse/sync';
import fs from 'node:fs';

const rows = parse(fs.readFileSync('data/logins.csv'), { columns: true }) as
  { username: string; password: string; valid: string }[];

for (const row of rows) {
  test(`csv login ${row.username}`, async ({ page }) => { /* ... */ });
}
```

### Faker for unique data

```
import { faker } from '@faker-js/faker';

export function newUser(overrides: Partial<User> = {}): User {
  return {
    username: faker.internet.username(),
    password: faker.internet.password({ length: 12 }),
    role: 'viewer',
    ...overrides,
  };
}
```

### Seed via API, assert via UI

```
test('order appears in the list', async ({ page, request }) => {
  const res = await request.post('/api/orders', { data: { sku: 'AB-1', qty: 2 } });
  expect(res.ok()).toBeTruthy();
  const { id } = await res.json();

  await page.goto('/orders');
  await expect(page.getByTestId(`order-${id}`)).toBeVisible();
});
```

Set up state through the fastest door (API/DB) and verify through the UI. It's faster and far less flaky than clicking through prerequisites.

## Authentication & storage state

Log in once, reuse the cookies/localStorage in every test — the single biggest speed win in most suites.

### Theory: session reuse without coupling

* **Storage state** is a JSON snapshot of cookies and origin storage. Injecting it into a context skips the login UI for every subsequent test.
* **Setup projects** run first (via `dependencies`) and write that file. Dependent projects load it with `use.storageState`.
* **Role isolation.** Keep separate states for admin/viewer/anonymous so permission tests stay honest.
* **UI login vs token inject.** Logging in through the UI validates the login journey once; API/token injection is faster for the rest of the suite. Use both deliberately.

```
// auth.setup.ts
import { test as setup, expect } from '@playwright/test';
const adminFile = '.auth/admin.json';

setup('login as admin', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.ADMIN_EMAIL!);
  await page.getByLabel('Password').fill(process.env.ADMIN_PASS!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('**/dashboard');
  await page.context().storageState({ path: adminFile });
});
```

```
// playwright.config.ts
projects: [
  { name: 'setup', testMatch: /auth\.setup\.ts/ },
  { name: 'admin-tests',
    testMatch: /.*admin.*\.spec\.ts/,
    use: { ...devices['Desktop Chrome'], storageState: '.auth/admin.json' },
    dependencies: ['setup'] },
  { name: 'anon-tests',
    testMatch: /.*public.*\.spec\.ts/,
    use: { storageState: { cookies: [], origins: [] } } },   // logged out
]
```

### Per-test override

```
test.use({ storageState: '.auth/viewer.json' });

test('viewer cannot see admin menu', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByRole('link', { name: 'Admin' })).toBeHidden();
});
```

### Token-based login (fastest)

```
const res = await request.post('/api/auth/login', {
  data: { email, password },
});
const { token } = await res.json();

await context.addInitScript(t => localStorage.setItem('token', t as string), token);
```

Storage state files contain live sessions — add `.auth/` to `.gitignore` and keep credentials in env vars or a secret manager.

## API testing

Playwright’s `request` fixture is an HTTP client that shares cookie jars with browser contexts when you want, but can also run pure API suites with no UI. Use it to validate contracts and to seed state for UI tests.

### Theory: where API tests fit

* **Faster feedback.** Status codes, headers and JSON schemas fail in milliseconds — push most backend rules here, not into slow browser journeys.
* **Same runner.** One report, one CI job model, shared env/config with UI tests.
* **Hybrid pattern.** `request.post` to create an order, then `page.goto` to assert it appears — best of both worlds.
* **Schema > snapshots of whole payloads.** Zod (or similar) documents the contract and tolerates additive fields better than brittle deep equality on every key.

```
import { test, expect } from '@playwright/test';

test.describe('Users API', () => {
  test('GET /users returns a page of users', async ({ request }) => {
    const res = await request.get('https://reqres.in/api/users', {
      params: { page: 2 },
      headers: { Accept: 'application/json' },
    });

    expect(res.status()).toBe(200);
    await expect(res).toBeOK();

    const body = await res.json() as { page: number; data: { id: number }[] };
    expect(body.page).toBe(2);
    expect(body.data.length).toBeGreaterThan(0);
    expect(res.headers()['content-type']).toContain('application/json');
  });

  test('POST /users creates a user', async ({ request }) => {
    const res = await request.post('https://reqres.in/api/users', {
      data: { name: 'Ada', job: 'engineer' },
    });
    expect(res.status()).toBe(201);
    expect(await res.json()).toMatchObject({ name: 'Ada', job: 'engineer' });
  });
});
```

### A reusable API context

```
import { request, type APIRequestContext } from '@playwright/test';

export const test = base.extend<{ api: APIRequestContext }>({
  api: async ({ playwright }, use) => {
    const ctx = await playwright.request.newContext({
      baseURL: process.env.API_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${process.env.API_TOKEN}` },
    });
    await use(ctx);
    await ctx.dispose();
  },
});
```

### Other request options

```
await request.put('/api/items/1',   { data: { qty: 3 } });
await request.patch('/api/items/1', { data: { qty: 4 } });
await request.delete('/api/items/1');
await request.post('/upload', { multipart: { file: { name: 'a.png', mimeType: 'image/png', buffer: buf } } });
await request.post('/form',   { form: { a: '1', b: '2' } });
await request.fetch('/any', { method: 'HEAD', timeout: 5000, failOnStatusCode: true });
```

### Schema validation with Zod

```
import { z } from 'zod';

const UserSchema = z.object({
  id: z.number(),
  email: z.string().email(),
  first_name: z.string(),
});

const parsed = UserSchema.safeParse((await res.json()).data);
expect(parsed.success, JSON.stringify(parsed.error?.issues)).toBe(true);
```

## Network interception & mocking

Playwright sits outside the browser and can see every request. That lets you stub backends, simulate failures, block trackers, rewrite responses, and replay HAR files — without changing application code.

### Theory: control the boundary

* **Mock to isolate UI.** When the test is about rendering/error states, fulfill a fake JSON response so the backend cannot flake the suite.
* **Do not mock what you claim to test.** If the journey is “checkout talks to payments”, prefer a real (or contract) service over a stub that always returns 200.
* **Abort noise.** Analytics and tag managers slow runs and add nondeterminism; aborting those hosts is a legitimate speed tactic.
* **HAR replay** freezes a known backend conversation for offline or demos — great for hermetic CI, weak if APIs change often (refresh with `update: true`).

```
// stub a JSON response
await page.route('**/api/products', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: 'Mocked widget', price: 99 }]),
  });
});

// simulate a server error
await page.route('**/api/checkout', route => route.fulfill({ status: 500, body: 'boom' }));

// block noisy third parties (speeds up runs a lot)
await page.route(/(analytics|googletagmanager|hotjar)\./, route => route.abort());

// modify a real response
await page.route('**/api/user', async route => {
  const res = await route.fetch();
  const json = await res.json();
  json.role = 'admin';
  await route.fulfill({ response: res, json });
});

// change the outgoing request
await page.route('**/api/**', route => route.continue({
  headers: { ...route.request().headers(), 'x-test': 'true' },
}));

// one-shot route, then remove
await page.route('**/api/flaky', route => route.abort(), { times: 1 });
await page.unroute('**/api/flaky');
```

### Inspecting traffic

```
page.on('request',  r => console.log('→', r.method(), r.url()));
page.on('response', r => console.log('←', r.status(), r.url()));
page.on('requestfailed', r => console.log('✗', r.url(), r.failure()?.errorText));
page.on('console', m => console.log('console:', m.type(), m.text()));
page.on('pageerror', e => console.log('JS error:', e.message));
```

### HAR record & replay

```
// record once
await page.routeFromHAR('har/api.har', { url: '**/api/**', update: true });
// replay offline afterwards (update: false)
await page.routeFromHAR('har/api.har', { url: '**/api/**' });
```

### Offline / slow network

```
await context.setOffline(true);
const client = await context.newCDPSession(page);      // Chromium only
await client.send('Network.emulateNetworkConditions', {
  offline: false, downloadThroughput: 50_000, uploadThroughput: 20_000, latency: 500,
});
```

## Visual & accessibility testing

Functional asserts catch “wrong text”. Visual and a11y checks catch “looks broken” and “unusable with assistive tech” — classes of bugs users notice immediately and unit tests miss.

### Theory: pixels and people

* **Screenshot comparison** diffs against a baseline image. Great for regressions in layout/CSS; sensitive to fonts, OS, and animations — hence Docker + masking dynamic regions.
* **Mask volatility.** Timestamps, avatars and ads should be masked or the suite becomes a noise generator.
* **Accessibility is a contract.** axe-core rules map to WCAG tags. Treat serious/critical violations like failing assertions, not optional warnings.
* **Complement, don’t replace.** Visual/a11y sit beside behavioural E2E — a green screenshot of a broken checkout flow is still a failure elsewhere.

### Screenshot comparison

```
await expect(page).toHaveScreenshot('dashboard.png', {
  fullPage: true,
  maxDiffPixelRatio: 0.02,
  animations: 'disabled',
  caret: 'hide',
  mask: [page.getByTestId('current-time'), page.getByRole('img', { name: 'avatar' })],
});

await expect(page.getByTestId('price-card')).toHaveScreenshot('price-card.png');
```

```
npx playwright test --update-snapshots        # regenerate baselines
npx playwright test --update-snapshots=changed
```

Baselines are OS- and browser-specific. Generate them in the same Docker image CI uses, or you will chase phantom diffs (font rendering).

### Accessibility with axe-core

```
npm i -D @axe-core/playwright
```

```
import AxeBuilder from '@axe-core/playwright';

test('home page has no serious a11y violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .exclude('#third-party-widget')
    .analyze();

  expect(results.violations.filter(v => v.impact === 'serious' || v.impact === 'critical')).toEqual([]);
});
```

### Ad-hoc screenshots & PDFs

```
await page.screenshot({ path: 'shots/home.png', fullPage: true });
await locator.screenshot({ path: 'shots/card.png' });
await page.pdf({ path: 'invoice.pdf', format: 'A4' });   // Chromium headless only
```

## Debugging & reporting

When a test fails, you need evidence: what the page looked like, which network calls ran, and which action timed out. Playwright’s tooling is built around that post-mortem loop.

### Theory: observe, then change

* **UI Mode / Inspector** are for local exploration — pick locators, step actions, watch the page.
* **Traces** are for CI: a zip with DOM snapshots, network, console and timeline. Prefer recording on retry so healthy runs stay light.
* **Flakes have causes.** Retries hide symptoms; traces reveal whether you raced an API, shared data, or asserted too early.
* **Reports are communication.** HTML/JUnit/blob reporters turn raw failures into something humans and dashboards can act on.

### The four tools

| Tool         | Command                             | Best for                                                     |
| ------------ | ----------------------------------- | ------------------------------------------------------------ |
| UI Mode      | npx playwright test --ui            | Watch mode, time-travel, pick locators, filter by tag        |
| Inspector    | npx playwright test --debug         | Step through actions, edit locators live                     |
| Trace Viewer | npx playwright show-trace trace.zip | Post-mortem of a CI failure: DOM snapshots, network, console |
| Codegen      | npx playwright codegen URL          | Recording a first draft of a flow                            |

```
await page.pause();                    // opens Inspector at this point
console.log(await page.content());
await page.screenshot({ path: 'debug.png' });
```

```
PWDEBUG=1 npx playwright test          # headed + inspector
DEBUG=pw:api npx playwright test       # verbose protocol logs
npx playwright test --trace on         # always record a trace
```

### Attaching artefacts to the report

```
test('with attachments', async ({ page }, testInfo) => {
  await page.goto('/');
  await testInfo.attach('homepage', {
    body: await page.screenshot(), contentType: 'image/png',
  });
  await testInfo.attach('api-response', {
    body: JSON.stringify({ ok: true }, null, 2), contentType: 'application/json',
  });
});
```

### Reporters

| Reporter          | Use                                                     |
| ----------------- | ------------------------------------------------------- |
| list / dot / line | Terminal output                                         |
| html              | Rich local report with traces & videos                  |
| junit             | Jenkins / GitLab / Azure test tabs                      |
| json              | Custom dashboards                                       |
| blob              | Merge results from shards: npx playwright merge-reports |
| allure-playwright | Allure reports (3rd-party)                              |

### Flake triage checklist

* Run `--repeat-each=10 --workers=1` to confirm it's real.
* Open the trace: which action timed out, what did the DOM look like?
* Look for hard sleeps, missing `await`, shared state between tests, order dependence.
* Check for animations/toasts intercepting clicks — assert on end state, not intermediate.
* Is the test relying on data another test created? Make it self-seeding.

## Sharding

Sharding splits one big Playwright suite across multiple machines (or containers) so wall-clock time drops roughly with the number of shards. Each machine runs a slice of the tests; you merge the results into one report at the end.

### Theory: workers vs shards

| Concept     | What it scales             | Where it runs                                             | Typical use               |
| ----------- | -------------------------- | --------------------------------------------------------- | ------------------------- |
| **Workers** | CPU cores on _one_ machine | Parallel processes in a single playwright test invocation | Local runs, single CI job |
| **Shards**  | Number of _machines_       | Separate jobs, each with \--shard=i/n                     | Large suites in CI        |

Workers and shards compose: each shard job can still use multiple workers. A 4-shard × 4-worker setup is \~16 concurrent tests (bounded by flakiness, app capacity, and licences).

**Mental model:** Playwright lists every test that would run, then assigns each test a stable index. Shard `i/n` keeps only tests whose index satisfies `index % n === i - 1`. Same suite + same filters ⇒ the same test always lands on the same shard.

### Core concepts

* **Shard index / total** — `--shard=2/4` means “piece 2 of 4”. Indexes are 1-based.
* **Deterministic split** — partitioning is by test list order after filters (`--grep`, projects, file paths). Do not rely on random assignment.
* **Independence required** — shards run at the same time against the same environment. Shared mutable accounts or order-dependent data will flake harder under sharding.
* **Blob reporter** — each shard writes a compact blob report; `merge-reports` rebuilds one HTML (or other) report for humans.
* **Balance** — equal count ≠ equal duration. One slow checkout flow can make shard 3 finish last. Prefer many small tests and `fullyParallel` so long tests do not monopolise a shard’s early slots as badly.

### Local CLI — try the concept

You can simulate sharding on one laptop by running three commands (sequentially or in three terminals). Each command only executes its third of the suite.

```
# Terminal / job 1 — first third of the suite
npx playwright test --shard=1/3

# Terminal / job 2
npx playwright test --shard=2/3

# Terminal / job 3
npx playwright test --shard=3/3

# Useful combos
npx playwright test --project=chromium --shard=1/4
npx playwright test --grep @smoke --shard=1/2
npx playwright test tests/checkout --shard=2/2
```

**Pitfall:** running `--shard=1/3` alone is _not_ a full suite — two-thirds of tests never ran. In CI, always spin up all `1..n` shard jobs.

### Config: enable blob reports for merging

```
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  fullyParallel: true,          // more even distribution inside files
  workers: process.env.CI ? 4 : undefined,
  retries: process.env.CI ? 2 : 0,

  reporter: process.env.CI
    ? [
        ['list'],
        ['blob', { outputDir: 'blob-report' }],  // one folder per shard job
      ]
    : [
        ['list'],
        ['html', { open: 'never' }],
      ],

  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
```

### End-to-end flow (concept → practice)

1. **Discover** — Playwright builds the full test list (after project / grep / path filters).
2. **Partition** — each job keeps only its shard’s tests via `--shard=i/n`.
3. **Execute** — each job runs with its own workers, traces, and blob output under `blob-report/`.
4. **Upload** — CI uploads each job’s blob folder as an artifact (unique name per shard).
5. **Merge** — a final job downloads all blobs and runs `merge-reports` to produce one HTML report.

### Merge reports after all shards finish

```
# After collecting every shard's blob-report into ./all-blob-reports
npx playwright merge-reports --reporter html ./all-blob-reports

# Other reporters work too
npx playwright merge-reports --reporter junit ./all-blob-reports
npx playwright merge-reports --reporter json ./all-blob-reports
```

```
// Optional: merge.config.ts if you need custom merge reporting
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'results/junit.xml' }],
  ],
});

// npx playwright merge-reports --config merge.config.ts ./all-blob-reports
```

### GitHub Actions matrix (complete example)

```
name: Playwright sharded
on:
  push: { branches: [main] }
  pull_request:

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false          # let other shards finish for a full report
      matrix:
        shardIndex: [1, 2, 3, 4]
        shardTotal: [4]         # keep total in one place
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps
      - name: Run shard ${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
        run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
        env:
          CI: true
          BASE_URL: ${{ vars.BASE_URL }}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: blob-report-${{ matrix.shardIndex }}
          path: blob-report
          retention-days: 7

  merge-report:
    if: always()
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - uses: actions/download-artifact@v4
        with:
          path: all-blob-reports
          pattern: blob-report-*
          merge-multiple: true
      - run: npx playwright merge-reports --reporter html ./all-blob-reports
      - uses: actions/upload-artifact@v4
        with:
          name: html-report
          path: playwright-report
```

### Sharding + projects + tags

```
# Each combination is a separate filtered list, then sharded
npx playwright test --project=chromium --grep @regression --shard=1/3
npx playwright test --project=chromium --grep @regression --shard=2/3
npx playwright test --project=chromium --grep @regression --shard=3/3

# Smoke on every PR (no shard or 2 shards); full regression nightly (many shards)
npx playwright test --grep @smoke
npx playwright test --grep @regression --shard=${SHARD}/8
```

**Pattern:** shard the _expensive_ regression suite; keep `@smoke` unsharded (or lightly sharded) so PR feedback stays simple and fast.

### Load balancing tips

* Enable `fullyParallel: true` so slow files do not pin an entire shard to a few long tests.
* Prefer many focused tests over one 15-minute mega-flow (or split that flow across files).
* Watch job durations in CI — if shard 4 always finishes 10 minutes after the others, split heavy files or raise shard count.
* Do not mix different `--grep` / project filters across shards of the same matrix; every job must use the _same_ filters and only vary `i` in `i/n`.

### Common mistakes

### Don't

* Run only shard `1/n` and call the pipeline green.
* Upload HTML reports per shard and never merge (hard to read).
* Share one login account that all shards mutate.
* Change `n` mid-matrix (job 1 uses `/3`, job 2 uses `/4`).
* Expect perfect time balance from equal test counts alone.

### Do

* Use identical CLI filters on every shard job.
* Emit `blob` reports and merge once.
* Seed unique data (API + faker) per test.
* Set `fail-fast: false` so you still get a full merged report.
* Keep shard total in one variable / matrix field.

### When sharding helps (and when it does not)

* **Helps** when suite duration is dominated by test count × browser time (hundreds of E2E tests).
* **Helps less** when the bottleneck is a shared staging app that cannot handle more parallel load — fix capacity or mock third parties first.
* **Overkill** for a 2-minute smoke suite; extra jobs add queue/setup overhead.

## CI/CD & Docker

CI is where E2E proves its value: every PR gets a repeatable signal. The theory is simple — same browsers, same env vars, parallel shards, artefacts on failure — so green means shippable and red is debuggable.

### Theory: make failures actionable

* **Parity.** Official Playwright Docker images match browser binaries to `@playwright/test`. Local/CI skew is a common source of “only fails in pipeline”.
* **Sharding** splits the suite across machines (`--shard=i/n`). See the dedicated Sharding topic for theory, local CLI practice, blob merge, and a full GitHub Actions matrix.
* **Retries ≠ quality.** A few CI retries catch infrastructure blips; chronic flakes need traces and test design fixes.
* **Secrets & config.** Credentials belong in CI secrets; base URLs in variables. Never commit storage-state files or passwords.

### GitHub Actions with sharding

```
name: Playwright Tests
on:
  push: { branches: [main] }
  pull_request:

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test --shard=${{ matrix.shard }}/4
        env:
          BASE_URL: ${{ vars.BASE_URL }}
          APP_USER: ${{ secrets.APP_USER }}
          APP_PASS: ${{ secrets.APP_PASS }}
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: blob-report-${{ matrix.shard }}
          path: blob-report
          retention-days: 7

  merge-report:
    if: always()
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - uses: actions/download-artifact@v4
        with: { path: all-blob-reports, pattern: blob-report-*, merge-multiple: true }
      - run: npx playwright merge-reports --reporter html ./all-blob-reports
      - uses: actions/upload-artifact@v4
        with: { name: html-report, path: playwright-report }
```

### Docker

```
FROM mcr.microsoft.com/playwright:v1.55.0-noble
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npx", "playwright", "test"]
```

```
docker run --rm -v $(pwd):/app -w /app \
  mcr.microsoft.com/playwright:v1.55.0-noble \
  sh -c "npm ci && npx playwright test"
```

Keep the Docker image tag in sync with your `@playwright/test` version, otherwise browser binaries and the client mismatch.

### CI hygiene

* `retries: 2` on CI, `0` locally.
* `forbidOnly: !!process.env.CI`.
* `trace: 'on-first-retry'`, `video: 'retain-on-failure'`.
* Cache `~/.cache/ms-playwright` or use the official image.
* Upload `playwright-report/` and `test-results/` as artifacts, always.
* Run `tsc --noEmit` and ESLint as separate jobs.

## Best practices

Good Playwright suites optimise for **signal**: failures mean a real user-visible problem, pass means you can ship. The practices below keep tests independent, readable, and cheap enough to run on every PR.

### Do

* Test user-visible behaviour, not implementation details.
* Prefer `getByRole`/`getByLabel`; add `data-testid` when needed.
* Keep tests independent and self-seeding — any order, any worker.
* Use web-first assertions and let auto-waiting do the work.
* Seed state via API/DB, verify via UI.
* Use fixtures + POM for reuse; keep specs declarative.
* Name tests by behaviour: "shows validation error when email is blank".
* Keep one logical flow per test; use `test.step` for readability.
* Run in CI on every PR with traces on retry.

### Don't

* `waitForTimeout()` as a fix for timing bugs.
* Brittle CSS/XPath chains tied to markup structure.
* Sharing logged-in state mutated across tests.
* `force: true` to bypass a real UI problem.
* Giant end-to-end tests that assert 20 unrelated things.
* Assertions inside page objects everywhere (mix responsibilities).
* Committing `test.only`, secrets, or `.auth/` files.
* Testing third-party sites you don't control in your critical suite.
* Chasing 100% E2E coverage — push detail down to unit tests.

### The test pyramid, applied

Many unit tests → fewer integration/component tests → a thin layer of E2E for critical user journeys (signup, login, search, checkout, payment). E2E is your smoke alarm, not your microscope.

### Suggested repo layout

```
e2e/
├─ tests/
│  ├─ auth/login.spec.ts
│  ├─ cart/checkout.spec.ts
│  └─ api/users.api.spec.ts
├─ pages/          # page objects
├─ components/     # component objects
├─ fixtures/       # custom fixtures
├─ data/           # json/csv + factories
├─ utils/          # helpers, env, api clients
├─ .auth/          # gitignored storage states
├─ playwright.config.ts
└─ tsconfig.json
```

## Cheat sheet

### Locators

| Goal             | Code                                        |
| ---------------- | ------------------------------------------- |
| Button by name   | page.getByRole('button', { name: 'Save' })  |
| Input by label   | page.getByLabel('Email')                    |
| Placeholder      | page.getByPlaceholder('Search')             |
| Text             | page.getByText('Welcome', { exact: true })  |
| Test id          | page.getByTestId('submit')                  |
| Nth              | loc.first() / .last() / .nth(2)             |
| Filter by text   | loc.filter({ hasText: 'Pro' })              |
| Filter by child  | loc.filter({ has: page.getByRole('img') })  |
| Inside container | page.getByRole('dialog').getByLabel('Name') |
| iframe           | page.frameLocator('#f').getByRole('button') |

### Actions

| Goal                   | Code                                           |
| ---------------------- | ---------------------------------------------- |
| Click / double / right | click() · dblclick() · click({button:'right'}) |
| Type fast / real keys  | fill('x') · pressSequentially('x')             |
| Key press              | press('Enter') · press('Control+A')            |
| Check / select         | check() · selectOption('IN')                   |
| Upload                 | setInputFiles('a.pdf')                         |
| Hover / drag           | hover() · dragTo(target)                       |
| Navigate               | page.goto('/x') · reload() · goBack()          |

### Assertions

| Goal               | Code                                            |
| ------------------ | ----------------------------------------------- |
| Visible / hidden   | toBeVisible() · toBeHidden()                    |
| Text               | toHaveText() · toContainText()                  |
| Value / count      | toHaveValue() · toHaveCount(3)                  |
| State              | toBeEnabled() · toBeChecked() · toBeEditable()  |
| Attr / class / css | toHaveAttribute() · toHaveClass() · toHaveCSS() |
| Page               | expect(page).toHaveURL() / toHaveTitle()        |
| API                | expect(res).toBeOK()                            |
| Soft               | expect.soft(loc).toBeVisible()                  |
| Poll / retry block | expect.poll(fn).toBe(x) · expect(fn).toPass()   |

### Test control

| Goal                | Code                                          |
| ------------------- | --------------------------------------------- |
| Group               | test.describe('x', () => {})                  |
| Hooks               | beforeAll · beforeEach · afterEach · afterAll |
| Skip / fixme / fail | test.skip() · test.fixme() · test.fail()      |
| Only                | test.only()                                   |
| Serial              | test.describe.serial()                        |
| Timeout             | test.setTimeout(60000) · test.slow()          |
| Per-file options    | test.use({ locale: 'fr-FR' })                 |
| Step                | await test.step('name', async () => {})       |

### CLI

```
npx playwright test                       # all
npx playwright test file.spec.ts:42       # single test by line
npx playwright test -g "@smoke"           # by title/tag
npx playwright test --project=firefox
npx playwright test --headed --workers=1
npx playwright test --ui | --debug
npx playwright test --repeat-each=5 --retries=0
npx playwright test --last-failed
npx playwright test --shard=1/4           # CI: job 1 of 4 machines
npx playwright merge-reports --reporter html ./all-blob-reports
npx playwright test --update-snapshots
npx playwright show-report
npx playwright codegen https://example.com
npx playwright install --with-deps
```

### Sharding (quick)

| Goal                  | Code                                                            |
| --------------------- | --------------------------------------------------------------- |
| Run slice of suite    | npx playwright test --shard=2/4                                 |
| Workers (one machine) | workers: 4 in config                                            |
| Shard artefacts       | reporter: \[\['blob', { outputDir: 'blob-report' }\]\]          |
| One HTML report       | npx playwright merge-reports --reporter html ./all-blob-reports |

## Interview questions & answers

30 questions that actually get asked, from screening to senior SDET rounds. Click to reveal.

### Fundamentals

1\. What is Playwright and how does it differ architecturally from Selenium?

Playwright is a Node.js-based automation library from Microsoft driving Chromium, Firefox and WebKit through a single API. It talks to browsers over a **WebSocket connection using browser dev-tools style protocols**, sending batched commands out-of-process. Selenium uses the **W3C WebDriver** HTTP protocol with a separate driver binary per browser. Practical consequences: Playwright is faster (fewer round trips), has built-in auto-waiting, network interception and browser contexts, whereas Selenium has broader language/browser/grid ecosystem support.

2\. Browser vs BrowserContext vs Page?

**Browser** is the launched browser process (expensive). **BrowserContext** is an isolated profile inside it — own cookies, localStorage, cache — cheap to create, like incognito. **Page** is a single tab in a context. Playwright gives each test a fresh context, which is how it achieves isolation without relaunching browsers.

3\. What is auto-waiting? Which checks does it perform?

Before every action Playwright retries a set of _actionability_ checks until they pass or the timeout expires: attached to DOM, visible, stable (bounding box unchanged across two animation frames), enabled, editable (for fill), and receives events (hit-target test). This removes most explicit waits.

4\. What makes an assertion "web-first"?

Assertions like `expect(locator).toBeVisible()` take a Locator and **retry the query** until the condition holds or `expect.timeout` (5 s default) is reached. Value assertions like `expect(5).toBe(5)` do not retry.

5\. Locator vs ElementHandle?

A Locator is a lazy selector re-evaluated at each use, so it never goes stale and it auto-waits. An ElementHandle points at a specific DOM node captured at a moment in time and breaks after re-render. Always use Locators; ElementHandle is legacy.

6\. What is strict mode?

Locators are strict by default: if the selector resolves to more than one element, an action throws a "strict mode violation" instead of silently acting on the first match. Resolve it by narrowing with `.filter()`, scoping to a parent, or explicitly using `.first()/.nth()`.

7\. Locator priority order you recommend?

getByRole → getByLabel / getByPlaceholder → getByText → getByAltText / getByTitle → getByTestId → CSS → XPath. Rationale: the higher options mirror how a real user (and assistive technology) identifies elements, so they survive refactors.

### Framework design

8\. Explain fixtures and why they beat beforeEach.

Fixtures are dependency-injected setup/teardown units created only when a test requests them. Benefits over hooks: composability (fixtures can depend on fixtures), lazy instantiation, worker- or test-scoped lifetimes, type safety, no shared mutable state in the file, and reuse across specs. `base.extend<T>()` creates your own typed test object.

9\. Test scope vs worker scope fixtures?

Test-scoped fixtures are created and torn down per test (default). Worker-scoped ones are created once per worker process and shared by every test that worker runs — good for expensive, read-only things like an auth token, seeded reference data or a DB connection. Never store mutable per-test state in a worker fixture.

10\. How do you implement the Page Object Model with TypeScript?

A class per page/component holding `readonly` `Locator` properties initialised in the constructor from the injected `Page`, plus methods expressing user intent (`login()`, `addToCart()`). Optionally a `BasePage` for shared navigation/utility. Page objects are then exposed to tests through custom fixtures so specs never construct them manually.

11\. Should assertions live inside page objects?

Keep the default in the test so intent is visible. It's acceptable to have explicit verification methods (`expectErrorShown()`) for repeated multi-step checks, but avoid burying business assertions where reviewers can't see them.

12\. How do you handle test data?

Prefer generated unique data (faker) plus API/DB seeding in fixtures, cleaned up in teardown. Static JSON/CSV for table-driven cases. Never depend on data another test created; never hard-code production records.

13\. How do you run the same tests against multiple environments/browsers?

Use `projects` in the config: each project sets its own `use` block (browser, device, baseURL, storageState, custom option fixtures). Environments come from env vars or a config map, selected with `--project`.

14\. What are project dependencies used for?

To run a setup project before dependent projects — typically an `auth.setup.ts` that logs in and writes `storageState`, or a data-seeding project. There is also `teardown` for cleanup after dependents finish.

### Execution & reliability

15\. How does parallelism work?

Playwright spawns worker processes (default ≈ half the CPU cores). Files run in parallel by default; with `fullyParallel: true` tests inside a file also run in parallel. Each test gets a fresh browser context. Control with `workers`, `test.describe.configure({ mode })`, and `--shard` for CI machines.

16\. How do you make tests independent?

No shared mutable globals; each test seeds its own data; auth via storageState rather than a UI login chain; no ordering assumptions; clean up in fixture teardown. Verify by running with `--workers=4 --repeat-each=3` and in random order.

17\. Retries — good or bad?

A pragmatic safety net on CI (`retries: 2`) that keeps infrastructure blips from blocking merges. Playwright marks tests that pass on retry as _flaky_ — treat that list as a bug backlog, not as green. Keep retries at 0 locally so flakiness is visible while writing tests.

18\. Describe your flaky-test triage process.

Reproduce with `--repeat-each`; open the trace to see the failing action and DOM snapshot; classify the cause (missing await, hard sleep, race with an animation/toast, shared state, real app race condition, third-party network); fix the root cause; add a targeted assertion; re-run repeatedly to confirm; track flake rate over time.

19\. Explain the timeout hierarchy.

Global timeout (whole run) > test timeout (30 s default) > action/navigation timeouts (0 = bounded only by the test) and expect timeout (5 s). A hook shares the test timeout budget. Raise them narrowly (`test.slow()`, per-assertion timeout) rather than globally.

20\. What does trace: 'on-first-retry' do and what's in a trace?

It records a trace only when a test is retried after failing — cheap in CI. The trace zip contains a timeline of actions, before/after/action DOM snapshots, screenshots, network requests, console logs, source and errors, viewable in Trace Viewer.

### Practical scenarios

21\. How do you handle authentication efficiently?

Log in once in a setup project, save `storageState()` to a JSON file, and point projects at it via `use.storageState`. For multiple roles, save one file per role. Even faster: obtain a token through the API and inject it with `addInitScript`.

22\. How do you handle iframes and new tabs?

iframes: `page.frameLocator('#id').getByRole(...)`, chained for nesting. New tabs: capture the `popup` event promise _before_ the click, then await it and treat it as a normal Page.

23\. File upload and download?

Upload: `setInputFiles()` on the file input, or the `filechooser` event for custom buttons; buffers work for synthetic files. Download: await the `download` event, then `download.saveAs()` / `path()` / `suggestedFilename()`.

24\. How do you mock an API response?

`await page.route('**/api/x', route => route.fulfill({ status: 200, json: {...} }))`. You can also `abort()` to simulate failures/block trackers, `continue()` with modified headers, or `fetch()` the real response and patch it. `routeFromHAR` replays recorded traffic.

25\. Can Playwright do API testing? Why bother inside an E2E suite?

Yes — the `request` fixture / `APIRequestContext` performs typed HTTP calls with cookies shared from the browser context if you want. It's used for fast setup/teardown, for asserting backend state after a UI action, and for pure API test suites — all in one framework and one report.

26\. How do you do visual regression testing?

`toHaveScreenshot()` compares against a committed baseline with configurable pixel/ratio thresholds, masking of dynamic regions and `animations: 'disabled'`. Baselines must be generated on the same OS/browser as CI — usually the official Docker image.

27\. How do you test a drag-and-drop or hover-only menu?

`dragTo()` first; if the app uses custom HTML5 DnD, do it manually with `hover() → mouse.down() → hover(target) → mouse.up()`, sometimes with intermediate mouse moves. Hover menus: `hover()` then assert the submenu is visible before clicking.

28\. How do you integrate Playwright into CI?

Node setup → `npm ci` → `npx playwright install --with-deps` (or the official Docker image) → run with shards → upload blob reports → merge into one HTML report → publish as an artifact. Secrets via CI secret store, `forbidOnly` and retries enabled on CI only.

29\. How do you decide what to automate in E2E?

Business-critical, high-traffic user journeys; regressions with real customer impact; flows that cross system boundaries. Push field-level validation, edge cases and error branches down to unit/component/API tests, which are faster and more stable.

30\. How would you scale a suite from 50 to 1000 tests?

Enforce structure (POM + fixtures + shared config), tag tests (@smoke/@regression) and run tiers on different triggers, shard across CI machines, use API seeding and storageState to cut runtime, mock unreliable third parties, enable blob-report merging, monitor duration & flake dashboards, and put ESLint + `tsc --noEmit` \+ code review standards around the test code itself — it's production code.

## Quiz — 20 questions

Score: **0** / 20 Reset 

## Resources

### Official

* Docs — Getting started
* API reference
* Best practices
* Release notes
* GitHub repo

### Practice sites

* TodoMVC (official demo)
* SauceDemo
* ExpandTesting
* The Internet (Heroku)
* ReqRes (fake REST API)

### Ecosystem packages

* `@axe-core/playwright` — accessibility
* `@faker-js/faker` — test data
* `allure-playwright` — reporting
* `zod` — API schema validation
* `dotenv` — env config
* `eslint-plugin-playwright` — lint rules

### Self-check before an interview

* Can you explain auto-waiting and the actionability checks?
* Can you write a custom fixture from memory?
* Can you set up storageState auth with project dependencies?
* Can you mock an API and assert the UI reaction?
* Can you read a trace and explain a failure?
* Can you write a GitHub Actions workflow with sharding?

 Built as offline study material for Playwright + TypeScript. API details reflect Playwright \~v1.4x–1.5x; always check the release notes for the newest additions.
