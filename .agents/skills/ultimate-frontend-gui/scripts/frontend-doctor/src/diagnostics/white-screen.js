import { join } from 'path';
import { existsSync } from 'fs';
import { detectFramework, findFiles, grepFiles, readText } from '../scanner.js';

export function diagnoseWhiteScreen(cwd) {
  const results = [];
  const { framework, buildTool, pkg, deps } = detectFramework(cwd);
  const htmlFiles = findFiles(cwd, ['.html']);
  const jsFiles = findFiles(cwd, ['.js', '.jsx', '.ts', '.tsx']);

  // Check: root element missing in HTML
  for (const file of htmlFiles) {
    const content = readText(file);
    if (!content) continue;
    const hasRoot = /id=["'](root|app|__next|__nuxt)["']/.test(content);
    if (!hasRoot && /<!DOCTYPE|<html/i.test(content)) {
      results.push({
        rootCause: 'Root mount element (#root / #app) missing in HTML',
        evidence: `${file} — no <div id="root"> or <div id="app"> found`,
        fix: 'Add <div id="root"></div> (or #app) inside <body> before your script tag',
      });
    }
  }

  // Check: env vars referenced but .env missing
  const envFile = join(cwd, '.env');
  const envLocalFile = join(cwd, '.env.local');
  const envPatterns = {
    vite: /import\.meta\.env\.\w+/,
    next: /process\.env\.NEXT_PUBLIC_\w+/,
    cra: /process\.env\.REACT_APP_\w+/,
  };
  for (const [tool, pattern] of Object.entries(envPatterns)) {
    const matches = grepFiles(jsFiles, pattern);
    if (matches.length > 0 && !existsSync(envFile) && !existsSync(envLocalFile)) {
      results.push({
        rootCause: `Environment variables referenced but no .env file found`,
        evidence: `${matches[0].file}:${matches[0].line} — ${matches[0].text}`,
        fix: `Create .env file with the required variables (${tool} prefix)`,
      });
      break;
    }
  }

  // Check: lazy import without error boundary (React)
  if (framework === 'react' || framework === 'next') {
    const lazyMatches = grepFiles(jsFiles, /React\.lazy\(|lazy\(/);
    if (lazyMatches.length > 0) {
      const suspenseMatches = grepFiles(jsFiles, /<Suspense/);
      if (suspenseMatches.length === 0) {
        results.push({
          rootCause: 'React.lazy() used without <Suspense> fallback',
          evidence: `${lazyMatches[0].file}:${lazyMatches[0].line} — ${lazyMatches[0].text}`,
          fix: 'Wrap lazy components with <Suspense fallback={<Loading />}>',
        });
      }
    }
    const boundaryMatches = grepFiles(jsFiles, /componentDidCatch|ErrorBoundary/);
    if (boundaryMatches.length === 0) {
      results.push({
        rootCause: 'No ErrorBoundary found — JS errors will cause white screen',
        evidence: 'No componentDidCatch or ErrorBoundary detected in source files',
        fix: 'Add an ErrorBoundary component at the root of your app to catch render errors',
      });
    }
  }

  // Check: Vue errorCaptured missing
  if (framework === 'vue' || framework === 'nuxt') {
    const errorHandlerMatches = grepFiles(jsFiles, /errorCaptured|app\.config\.errorHandler/);
    if (errorHandlerMatches.length === 0) {
      results.push({
        rootCause: 'No global error handler — Vue errors may cause white screen',
        evidence: 'No errorCaptured hook or app.config.errorHandler found',
        fix: 'Add app.config.errorHandler in your main entry or use errorCaptured in root component',
      });
    }
  }

  // Check: SPA history fallback missing
  if (buildTool === 'vite') {
    const viteConfig = readText(join(cwd, 'vite.config.ts')) || readText(join(cwd, 'vite.config.js'));
    if (viteConfig && !/historyApiFallback/.test(viteConfig)) {
      const routerUsed = grepFiles(jsFiles, /createBrowserRouter|BrowserRouter|createRouter.*history/);
      if (routerUsed.length > 0) {
        results.push({
          rootCause: 'SPA router detected but no history fallback configured — refresh will 404',
          evidence: `${routerUsed[0].file}:${routerUsed[0].line} — ${routerUsed[0].text}`,
          fix: 'For dev: add server.historyApiFallback in vite.config. For prod: configure try_files in nginx/server',
        });
      }
    }
  }

  return results;
}
