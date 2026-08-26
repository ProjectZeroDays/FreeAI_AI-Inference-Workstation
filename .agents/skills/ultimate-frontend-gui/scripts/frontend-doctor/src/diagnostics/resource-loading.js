import { join } from 'path';
import { detectFramework, findFiles, grepFiles, readText, readJson } from '../scanner.js';

export function diagnoseResourceLoading(cwd) {
  const results = [];
  const { buildTool } = detectFramework(cwd);
  const cssFiles = findFiles(cwd, ['.css', '.scss', '.less']);
  const configFiles = findFiles(cwd, ['.js', '.ts', '.mjs']);

  // Check: vite base path
  if (buildTool === 'vite') {
    const viteConfig = readText(join(cwd, 'vite.config.ts')) || readText(join(cwd, 'vite.config.js'));
    if (viteConfig && !/base\s*:/.test(viteConfig)) {
      results.push({
        rootCause: 'Vite config missing "base" — assets may 404 when deployed to a subdirectory',
        evidence: 'vite.config.{ts,js} — no base property found',
        fix: 'Add base: "/your-subpath/" to vite.config if deploying to a subdirectory',
      });
    }
  }

  // Check: webpack publicPath
  if (buildTool === 'webpack') {
    const wpConfig = readText(join(cwd, 'webpack.config.js'));
    if (wpConfig && !/publicPath/.test(wpConfig)) {
      results.push({
        rootCause: 'Webpack config missing output.publicPath — assets may load from wrong path',
        evidence: 'webpack.config.js — no publicPath in output config',
        fix: 'Add output.publicPath: "/" or your deploy path to webpack.config.js',
      });
    }
  }

  // Check: next.js assetPrefix
  if (buildTool === 'next') {
    const nextConfig = readText(join(cwd, 'next.config.js')) || readText(join(cwd, 'next.config.mjs'));
    if (nextConfig && /assetPrefix/.test(nextConfig)) {
      const hasTrailingSlash = /assetPrefix\s*:\s*['"][^'"]+\/['"]/.test(nextConfig);
      if (!hasTrailingSlash) {
        results.push({
          rootCause: 'next.config assetPrefix may be missing trailing slash',
          evidence: 'next.config.{js,mjs} — assetPrefix found without trailing slash',
          fix: 'Ensure assetPrefix ends with / e.g. "https://cdn.example.com/"',
        });
      }
    }
  }

  // Check: font/image paths in CSS using absolute paths without base
  const badPaths = grepFiles(cssFiles, /url\(\s*['"]?\//);
  if (badPaths.length > 0) {
    results.push({
      rootCause: 'CSS url() uses absolute path — may break in subdirectory deployments',
      evidence: `${badPaths[0].file}:${badPaths[0].line} — ${badPaths[0].text}`,
      fix: 'Use relative paths in CSS url() or ensure build tool rewrites them correctly',
    });
  }

  // Check: mixed content (http in https context)
  const allFiles = findFiles(cwd, ['.js', '.jsx', '.ts', '.tsx', '.html', '.css']);
  const httpRefs = grepFiles(allFiles, /["']http:\/\/(?!localhost)/);
  if (httpRefs.length > 0) {
    results.push({
      rootCause: 'HTTP resource referenced — will be blocked on HTTPS pages (mixed content)',
      evidence: `${httpRefs[0].file}:${httpRefs[0].line} — ${httpRefs[0].text}`,
      fix: 'Change http:// to https:// or use protocol-relative // URLs',
    });
  }

  return results;
}
