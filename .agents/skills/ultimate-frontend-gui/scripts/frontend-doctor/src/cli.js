#!/usr/bin/env node
import { resolve } from 'path';
import { diagnoseWhiteScreen } from './diagnostics/white-screen.js';
import { diagnoseJsErrors } from './diagnostics/js-errors.js';
import { diagnoseResourceLoading } from './diagnostics/resource-loading.js';
import { diagnoseHydration } from './diagnostics/hydration.js';
import { diagnoseCssLayout } from './diagnostics/css-layout.js';
import { diagnoseExtensionPopup } from './diagnostics/extension-popup.js';
import { formatReport } from './report.js';

const cwd = resolve(process.argv[2] || '.');

console.log(`\n  \x1b[1mfrontend-doctor\x1b[0m  scanning ${cwd} ...\n`);

const results = [
  ...diagnoseWhiteScreen(cwd),
  ...diagnoseJsErrors(cwd),
  ...diagnoseResourceLoading(cwd),
  ...diagnoseHydration(cwd),
  ...diagnoseCssLayout(cwd),
  ...diagnoseExtensionPopup(cwd),
];

formatReport(results);

process.exit(results.length > 0 ? 1 : 0);
