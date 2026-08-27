---
name: playwright
description: "Browser automation with Playwright. Use when the user asks to test a website, take screenshots, check responsive design, test login flows, fill forms, check broken links, or automate any browser task."
metadata:
  version: 1.0.0
---

# Playwright (Browser Automation)

General-purpose browser automation skill. Write custom Playwright scripts for any automation task and execute them via the universal executor.

## Trigger

Any user request involving browser testing, web automation, screenshots, responsive design checks, form testing, link validation, login flow testing, or any other browser-based task.

## Workflow

### 1. Resolve skill directory

This skill can be installed in different locations (plugin system, manual installation, global, or project-specific). Determine the skill directory based on where this SKILL.md was loaded. Use that path as `$SKILL_DIR` in all commands below.

### 2. Setup (first time only)

```bash
cd $SKILL_DIR && npm run setup
```

Installs Playwright and Chromium. Only needed once.

### 3. Detect dev servers

For localhost testing, always detect running servers first:

```bash
cd $SKILL_DIR && node -e "require('./lib/helpers').detectDevServers().then(servers => console.log(JSON.stringify(servers)))"
```

| Result | Action |
|--------|--------|
| 1 server found | Use it automatically, inform user |
| Multiple servers found | Ask user which one to test |
| No servers found | Ask for URL or offer to help start dev server |

### 4. Write the test script

Write custom Playwright code to `/tmp/playwright-test-*.js`. Never write test files to the skill directory or user's project.

Rules:
- Parameterize URLs — put detected/provided URL in a `TARGET_URL` constant at top
- Use `headless: false` by default — only use headless when user explicitly requests it
- Use `slowMo: 100` for visibility when helpful

### 5. Execute

```bash
cd $SKILL_DIR && node run.js /tmp/playwright-test-page.js
```

For quick one-off tasks, execute inline without creating files:

```bash
cd $SKILL_DIR && node run.js "
const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();
await page.goto('http://localhost:3001');
await page.screenshot({ path: '/tmp/quick-screenshot.png', fullPage: true });
console.log('Screenshot saved');
await browser.close();
"
```

| Input method | When to use |
|-------------|-------------|
| File (`/tmp/playwright-test-*.js`) | Complex tests, responsive checks, anything user might re-run |
| Inline string | Quick one-off tasks (screenshot, check element, get page title) |

### 6. Report results

Display results in real-time. Browser window is visible for debugging. Test files in `/tmp` are auto-cleaned by the OS.

## Common Patterns

### Test a page (multiple viewports)

```javascript
// /tmp/playwright-test-responsive.js
const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:3001'; // Auto-detected

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();

  // Desktop test
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.goto(TARGET_URL);
  console.log('Desktop - Title:', await page.title());
  await page.screenshot({ path: '/tmp/desktop.png', fullPage: true });

  // Mobile test
  await page.setViewportSize({ width: 375, height: 667 });
  await page.screenshot({ path: '/tmp/mobile.png', fullPage: true });

  await browser.close();
})();
```

### Test login flow

```javascript
// /tmp/playwright-test-login.js
const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:3001'; // Auto-detected

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto(`${TARGET_URL}/login`);

  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Wait for redirect
  await page.waitForURL('**/dashboard');
  console.log('Login successful, redirected to dashboard');

  await browser.close();
})();
```

### Fill and submit form

```javascript
// /tmp/playwright-test-form.js
const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:3001'; // Auto-detected

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 50 });
  const page = await browser.newPage();

  await page.goto(`${TARGET_URL}/contact`);

  await page.fill('input[name="name"]', 'John Doe');
  await page.fill('input[name="email"]', 'john@example.com');
  await page.fill('textarea[name="message"]', 'Test message');
  await page.click('button[type="submit"]');

  // Verify submission
  await page.waitForSelector('.success-message');
  console.log('Form submitted successfully');

  await browser.close();
})();
```

### Check for broken links

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto('http://localhost:3000');

  const links = await page.locator('a[href^="http"]').all();
  const results = { working: 0, broken: [] };

  for (const link of links) {
    const href = await link.getAttribute('href');
    try {
      const response = await page.request.head(href);
      if (response.ok()) {
        results.working++;
      } else {
        results.broken.push({ url: href, status: response.status() });
      }
    } catch (e) {
      results.broken.push({ url: href, error: e.message });
    }
  }

  console.log(`Working links: ${results.working}`);
  console.log(`Broken links:`, results.broken);

  await browser.close();
})();
```

### Take screenshot with error handling

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    await page.goto('http://localhost:3000', {
      waitUntil: 'networkidle',
      timeout: 10000,
    });

    await page.screenshot({
      path: '/tmp/screenshot.png',
      fullPage: true,
    });

    console.log('Screenshot saved to /tmp/screenshot.png');
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
})();
```

### Test responsive design

```javascript
// /tmp/playwright-test-responsive-full.js
const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:3001'; // Auto-detected

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  const viewports = [
    { name: 'Desktop', width: 1920, height: 1080 },
    { name: 'Tablet', width: 768, height: 1024 },
    { name: 'Mobile', width: 375, height: 667 },
  ];

  for (const viewport of viewports) {
    console.log(
      `Testing ${viewport.name} (${viewport.width}x${viewport.height})`,
    );

    await page.setViewportSize({
      width: viewport.width,
      height: viewport.height,
    });

    await page.goto(TARGET_URL);
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: `/tmp/${viewport.name.toLowerCase()}.png`,
      fullPage: true,
    });
  }

  console.log('All viewports tested');
  await browser.close();
})();
```

## Available Helpers

Optional utility functions in `lib/helpers.js`:

```javascript
const helpers = require('./lib/helpers');

// Detect running dev servers (use this first)
const servers = await helpers.detectDevServers();
console.log('Found servers:', servers);

// Safe click with retry
await helpers.safeClick(page, 'button.submit', { retries: 3 });

// Safe type with clear
await helpers.safeType(page, '#username', 'testuser');

// Take timestamped screenshot
await helpers.takeScreenshot(page, 'test-result');

// Handle cookie banners
await helpers.handleCookieBanner(page);

// Extract table data
const data = await helpers.extractTableData(page, 'table.results');
```

See `lib/helpers.js` for full list.

## Custom HTTP Headers

Configure custom headers for all HTTP requests via environment variables. Useful for identifying automated traffic, getting LLM-optimized responses, or adding authentication tokens globally.

**Single header (common case):**

```bash
cd $SKILL_DIR && \
  PW_HEADER_NAME=X-Automated-By PW_HEADER_VALUE=playwright-skill \
  node run.js /tmp/my-script.js
```

**Multiple headers (JSON format):**

```bash
cd $SKILL_DIR && \
  PW_EXTRA_HEADERS='{"X-Automated-By":"playwright-skill","X-Debug":"true"}' \
  node run.js /tmp/my-script.js
```

Headers are automatically applied when using `helpers.createContext()`:

```javascript
const context = await helpers.createContext(browser);
const page = await context.newPage();
// All requests from this page include your custom headers
```

For scripts using raw Playwright API, use the injected `getContextOptionsWithHeaders()`:

```javascript
const context = await browser.newContext(
  getContextOptionsWithHeaders({ viewport: { width: 1920, height: 1080 } }),
);
```

## Advanced Usage

For comprehensive Playwright API documentation, see [API_REFERENCE.md](API_REFERENCE.md):

- Selectors & Locators best practices
- Network interception & API mocking
- Authentication & session management
- Visual regression testing
- Mobile device emulation
- Performance testing
- Debugging techniques
- CI/CD integration

## Notes

- Each automation is custom-written for the specific request — not limited to pre-built scripts.
- Auto-detects running dev servers to eliminate hardcoded URLs.
- Test scripts written to `/tmp` for automatic cleanup (no project clutter).
- Code executes with proper module resolution via `run.js`.
- API_REFERENCE.md loaded only when advanced features are needed.
- Use `waitForURL`, `waitForSelector`, `waitForLoadState` instead of fixed timeouts.
- Always use try-catch for robust automation.
- **Playwright not installed?** Run `cd $SKILL_DIR && npm run setup`.
- **Module not found?** Ensure running from skill directory via `run.js` wrapper.
- **Browser doesn't open?** Check `headless: false` and ensure display is available.
- **Element not found?** Add wait: `await page.waitForSelector('.element', { timeout: 10000 })`.
