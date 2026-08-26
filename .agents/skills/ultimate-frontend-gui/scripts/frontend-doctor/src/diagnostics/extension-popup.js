import { join } from 'path';
import { existsSync } from 'fs';
import { findFiles, grepFiles, readJson, readText } from '../scanner.js';

export function diagnoseExtensionPopup(cwd) {
  const results = [];
  const manifest = readJson(join(cwd, 'manifest.json'));
  if (!manifest || !manifest.manifest_version) return results;

  const isV3 = manifest.manifest_version === 3;
  const jsFiles = findFiles(cwd, ['.js', '.ts', '.jsx', '.tsx']);
  const htmlFiles = findFiles(cwd, ['.html']);

  // Check: popup HTML missing or misconfigured
  const popupPath = manifest.action?.default_popup || manifest.browser_action?.default_popup;
  if (popupPath) {
    if (!existsSync(join(cwd, popupPath))) {
      results.push({
        rootCause: 'Popup HTML file referenced in manifest does not exist',
        evidence: `manifest.json — default_popup: "${popupPath}" not found`,
        fix: `Create the file at ${popupPath}`,
      });
    }
  } else {
    if (isV3 && !manifest.action) {
      results.push({
        rootCause: 'MV3 manifest missing "action" field — popup will not appear',
        evidence: 'manifest.json — no "action" key found',
        fix: 'Add "action": { "default_popup": "popup.html" } to manifest.json',
      });
    }
    if (!isV3 && !manifest.browser_action) {
      results.push({
        rootCause: 'MV2 manifest missing "browser_action" — popup will not appear',
        evidence: 'manifest.json — no "browser_action" key found',
        fix: 'Add "browser_action": { "default_popup": "popup.html" } to manifest.json',
      });
    }
  }

  // Check: CSP blocks inline scripts (MV3 default)
  if (isV3) {
    for (const file of htmlFiles) {
      const content = readText(file);
      if (content && /<script(?!\s+src)[^>]*>[\s\S]+?<\/script>/.test(content)) {
        results.push({
          rootCause: 'Inline script in MV3 extension — blocked by Content Security Policy',
          evidence: `${file} — inline <script> tag found`,
          fix: 'Move inline scripts to separate .js files and reference with <script src="...">',
        });
        break;
      }
    }
  }

  // Check: popup uses localStorage instead of chrome.storage
  const localStorageUse = grepFiles(jsFiles, /localStorage\.(get|set)Item/);
  if (localStorageUse.length > 0) {
    results.push({
      rootCause: 'localStorage used in extension — data is scoped to popup and lost when closed',
      evidence: `${localStorageUse[0].file}:${localStorageUse[0].line} — ${localStorageUse[0].text}`,
      fix: 'Use chrome.storage.local or chrome.storage.sync for persistent extension data',
    });
  }

  // Check: MV3 using chrome.browserAction (removed in MV3)
  if (isV3) {
    const oldApi = grepFiles(jsFiles, /chrome\.browserAction/);
    if (oldApi.length > 0) {
      results.push({
        rootCause: 'chrome.browserAction used in MV3 — API removed, use chrome.action instead',
        evidence: `${oldApi[0].file}:${oldApi[0].line} — ${oldApi[0].text}`,
        fix: 'Replace chrome.browserAction with chrome.action (MV3)',
      });
    }
  }

  // Check: missing permissions for APIs used
  const permissions = manifest.permissions || [];
  const apiPermMap = {
    'chrome.tabs': 'tabs',
    'chrome.storage': 'storage',
    'chrome.alarms': 'alarms',
    'chrome.notifications': 'notifications',
    'chrome.cookies': 'cookies',
  };
  for (const [api, perm] of Object.entries(apiPermMap)) {
    const usage = grepFiles(jsFiles, new RegExp(api.replace('.', '\\.')));
    if (usage.length > 0 && !permissions.includes(perm)) {
      results.push({
        rootCause: `${api} used but "${perm}" permission not declared`,
        evidence: `${usage[0].file}:${usage[0].line} — ${usage[0].text}`,
        fix: `Add "${perm}" to permissions array in manifest.json`,
      });
    }
  }

  return results;
}
