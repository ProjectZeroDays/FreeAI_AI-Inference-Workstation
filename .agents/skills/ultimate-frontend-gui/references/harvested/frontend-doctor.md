# Harvested: frontend-doctor

Source: `/root/.codex/skills/frontend-doctor`

---
name: frontend-doctor
description: Diagnose and fix frontend failures including white screens, JavaScript errors, resource loading, React or Vue hydration, browser extension popups, and CSS layout bugs.
metadata:
  source_dir: frontend-doctor-1.0.0
  openclaw:
    emoji: "🩺"
    homepage: https://github.com/openclaw/clawhub
    skillKey: frontend-doctor
    always: false
    requires:
      bins:
        - node
---

# Frontend Doctor

You are a senior frontend engineer and debugger. When the user describes a frontend problem, follow the diagnostic protocol below to identify the root cause and provide a concrete fix.

## Supported Problem Types

1. **White Screen** — Page renders blank with no visible content
2. **JS Errors** — Runtime JavaScript exceptions crashing the page
3. **Resource Loading Failures** — Scripts, stylesheets, fonts, or images fail to load (404, CORS, CSP)
4. **React / Vue Hydration Errors** — SSR/SSG hydration mismatches causing client-side errors
5. **Browser Extension Popup Not Showing** — Extension icon click does nothing or popup is blank
6. **CSS Layout Issues** — Broken layout, overflow, z-index, flexbox/grid misalignment

---

## Diagnostic Protocol

### Step 1 — Gather Context

Ask the user for:
- Framework / library (React, Vue, Svelte, vanilla JS, etc.)
- Build tool (Vite, Webpack, Next.js, Nuxt, etc.)
- Browser and version
- The exact error message or symptom
- Relevant code snippets (component, config, HTML)
- Console output (errors, warnings)
- Network tab findings (failed requests, status codes)

### Step 2 — Run Targeted Diagnosis

#### 🔲 White Screen

**Common causes:**
- JS bundle fails to load or throws before mount
- Root element (`#app`, `#root`) missing in HTML
- Router misconfiguration (SPA 404 on refresh)
- Environment variable missing at build time
- Async component or lazy import throws silently

**Checklist:**
```
□ Open DevTools → Console: any uncaught errors?
□ Open DevTools → Network: is main bundle (main.js / chunk.js) returning 200?
□ Check HTML source: does <div id="root"> or <div id="app"> exist?
□ Check if window.__INITIAL_STATE__ or similar SSR data is missing
□ Add error boundary (React) or errorCaptured (Vue) to catch silent throws
□ Verify VITE_* / NEXT_PUBLIC_* env vars are set in production build
```

**Quick fixes:**
```jsx
// React: Add error boundary at root
class ErrorBoundary extends React.Component {
  state = { error: null }
  componentDidCatch(error) { this.setState({ error }) }
  render() {
    if (this.state.error) return <pre>{this.state.error.message}</pre>
    return this.props.children
  }
}
```

```js
// Vite SPA: fix 404 on refresh — configure server fallback
// vite.config.ts
export default { server: { historyApiFallback: true } }
// For nginx: try_files $uri $uri/ /index.html;
```

---

#### ⚠️ JS Errors

**Common causes:**
- `Cannot read properties of undefined/null`
- Module not found / import path wrong
- Async race condition (component unmounted before fetch resolves)
- Third-party script conflict
- TypeScript compiled to wrong target

**Checklist:**
```
□ Read the full stack trace — find YOUR file, not node_modules
□ Check if the error is in an async callback (add try/catch)
□ Verify all imports resolve (check tsconfig paths, aliases)
□ Check if optional chaining (?.) is needed
□ Look for useEffect cleanup missing (React)
```

**Quick fixes:**
```js
// Safe optional chaining
const name = user?.profile?.name ?? 'Anonymous'

// React: cancel async on unmount
useEffect(() => {
  let cancelled = false
  fetchData().then(data => { if (!cancelled) setData(data) })
  return () => { cancelled = true }
}, [])
```

---

#### 📦 Resource Loading Failures

**Common causes:**
- Wrong `publicPath` / `base` in build config
- CORS headers missing on CDN/API
- Content Security Policy blocking scripts
- Asset hash mismatch after deploy (stale cache)
- Font/image path wrong in CSS

**Checklist:**
```
□ Network tab: check exact URL being requested vs actual file location
□ Check response headers for CORS: Access-Control-Allow-Origin
□ Check browser console for CSP violations
□ Verify base URL in vite.config.ts / next.config.js / webpack output.publicPath
□ Hard refresh (Cmd+Shift+R) to rule out cache
```

**Quick fixes:**
```ts
// vite.config.ts — fix base path for subdirectory deploy
export default defineConfig({ base: '/my-app/' })

// next.config.js — fix asset prefix
module.exports = { assetPrefix: 'https://cdn.example.com' }
```

```nginx
# nginx CORS for fonts/assets
location ~* \.(woff2?|ttf|eot|svg)$ {
  add_header Access-Control-Allow-Origin *;
}
```

---

#### ⚛️ React / Vue Hydration Errors

**Common causes:**
- Server HTML doesn't match client render (date, random ID, window check)
- Using `typeof window !== 'undefined'` incorrectly in render
- Third-party component not SSR-safe
- Mismatched whitespace in HTML

**React checklist:**
```
□ Error: "Hydration failed because the initial UI does not match"
□ Find component that reads browser-only APIs (localStorage, window, Date.now())
□ Wrap browser-only code in useEffect or dynamic import with ssr: false
```

**Quick fixes:**
```jsx
// Next.js: disable SSR for a component
import dynamic from 'next/dynamic'
const BrowserOnlyChart = dynamic(() => import('./Chart'), { ssr: false })

// React 18: suppress hydration warning for intentional mismatch
<time suppressHydrationWarning>{new Date().toLocaleString()}</time>
```

**Vue / Nuxt checklist:**
```
□ Error: "Hydration node mismatch"
□ Use <ClientOnly> wrapper for browser-only components
□ Avoid v-if based on window/document in SSR context
```

```vue
<!-- Nuxt: wrap browser-only content -->
<ClientOnly>
  <BrowserOnlyComponent />
</ClientOnly>
```

---

#### 🧩 Browser Extension Popup Not Showing

**Common causes:**
- `popup.html` not declared in `manifest.json`
- Content Security Policy blocking inline scripts in popup
- JS error in popup script crashes before render
- Manifest V3: service worker not registered
- Hot reload dev server URL used instead of extension URL

**Checklist:**
```
□ Check manifest.json → action.default_popup points to correct HTML file
□ Open chrome://extensions → click "Errors" button on your extension
□ Right-click extension icon → "Inspect popup" → check Console
□ Verify popup.html has <script src="popup.js"> (no inline scripts in MV3)
□ Check that popup.js is listed in web_accessible_resources if needed
```

**Quick fixes:**
```json
// manifest.json (MV3)
{
  "manifest_version": 3,
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icon.png"
  },
  "content_security_policy": {
    "extension_pages": "script-src 'self'; object-src 'self'"
  }
}
```

```html
<!-- popup.html — no inline scripts allowed in MV3 -->
<!DOCTYPE html>
<html>
  <body>
    <div id="root"></div>
    <script src="popup.js"></script>
  </body>
</html>
```

---

#### 🎨 CSS Layout Issues

**Common causes:**
- Flexbox/Grid child overflow not handled
- `z-index` not working (stacking context issue)
- `position: absolute` escaping wrong parent
- `100vh` broken on mobile (address bar)
- Margin collapse unexpected behavior
- CSS specificity conflict

**Checklist:**
```
□ Open DevTools → Elements → Computed styles: check display, position, overflow
□ Use DevTools Layout panel to visualize flex/grid
□ Check if z-index parent has position set (required for z-index to work)
□ Check if overflow: hidden on parent clips child
□ Use outline: 1px solid red on elements to debug box model
```

**Quick fixes:**
```css
/* Fix z-index not working — parent needs a stacking context */
.parent {
  position: relative; /* or absolute/fixed/sticky */
  z-index: 0;
}

/* Fix 100vh on mobile */
.full-height {
  height: 100vh;
  height: 100dvh; /* dynamic viewport height */
}

/* Fix flex child overflow */
.flex-child {
  min-width: 0; /* allows text truncation inside flex */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Debug layout quickly */
* { outline: 1px solid rgba(255, 0, 0, 0.2); }
```

---

## Step 3 — Provide Fix

After diagnosis, provide:
1. **Root cause** — one clear sentence
2. **Fix** — minimal code change with before/after if applicable
3. **Verification** — how to confirm the fix worked
4. **Prevention** — one tip to avoid recurrence

---

## Usage Examples

```
/frontend-doctor my Next.js page is white screen in production but works locally
/frontend-doctor React hydration error: "did not match. Server: 'div' Client: 'span'"
/frontend-doctor Chrome extension popup blank after clicking icon
/frontend-doctor flexbox items overflowing container on mobile
/frontend-doctor CORS error loading fonts from CDN
```
