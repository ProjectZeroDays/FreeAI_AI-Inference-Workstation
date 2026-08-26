import { existsSync } from 'fs';
import { detectFramework, findFiles, grepFiles } from '../scanner.js';

export function diagnoseJsErrors(cwd) {
  const results = [];
  const { framework } = detectFramework(cwd);
  const jsFiles = findFiles(cwd, ['.js', '.jsx', '.ts', '.tsx']);

  // Check: unguarded property access patterns
  const unsafeAccess = grepFiles(jsFiles, /\w+\.\w+\.\w+(?!\?)/ );
  const deepChains = unsafeAccess.filter(m =>
    !m.text.includes('?.') &&
    /\w+\.\w+\.\w+\.\w+/.test(m.text) &&
    !m.text.startsWith('//') &&
    !m.text.startsWith('*') &&
    !m.text.includes('console.') &&
    !m.text.includes('import') &&
    !m.text.includes('require')
  );
  if (deepChains.length > 0) {
    const sample = deepChains[0];
    results.push({
      rootCause: 'Deep property access without optional chaining — risk of "Cannot read properties of undefined"',
      evidence: `${sample.file}:${sample.line} — ${sample.text}`,
      fix: 'Use optional chaining (?.) for nested property access, e.g. obj?.nested?.prop',
    });
  }

  // Check: async without try/catch
  const asyncNoTry = grepFiles(jsFiles, /async\s+\w+|async\s*\(/);
  if (asyncNoTry.length > 0) {
    const tryCatches = grepFiles(jsFiles, /try\s*\{/);
    if (tryCatches.length === 0 && asyncNoTry.length > 2) {
      results.push({
        rootCause: 'Async functions found but no try/catch blocks — unhandled promise rejections likely',
        evidence: `${asyncNoTry[0].file}:${asyncNoTry[0].line} — ${asyncNoTry[0].text}`,
        fix: 'Wrap async operations in try/catch or add .catch() to promise chains',
      });
    }
  }

  // Check: useEffect without cleanup (React)
  if (framework === 'react' || framework === 'next') {
    const effectsWithFetch = grepFiles(jsFiles, /useEffect\s*\(\s*\(\)\s*=>\s*\{[\s\S]*fetch/);
    const effectCleanups = grepFiles(jsFiles, /return\s*\(\)\s*=>\s*\{/);
    if (effectsWithFetch.length > 0 && effectCleanups.length === 0) {
      results.push({
        rootCause: 'useEffect with fetch but no cleanup — may update state on unmounted component',
        evidence: `${effectsWithFetch[0].file}:${effectsWithFetch[0].line} — ${effectsWithFetch[0].text}`,
        fix: 'Add cleanup: useEffect(() => { let cancelled = false; fetch().then(d => { if (!cancelled) set(d) }); return () => { cancelled = true } }, [])',
      });
    }
  }

  // Check: tsconfig target too low
  const tsFiles = findFiles(cwd, ['.ts', '.tsx']);
  if (tsFiles.length > 0) {
    const tsconfig = grepFiles([cwd + '/tsconfig.json'].filter(f => existsSync(f)), /"target"\s*:\s*"(es5|es3)"/i);
    if (tsconfig.length > 0) {
      results.push({
        rootCause: 'TypeScript target set too low — modern syntax may not compile correctly',
        evidence: `${tsconfig[0].file}:${tsconfig[0].line} — ${tsconfig[0].text}`,
        fix: 'Update tsconfig.json target to "es2017" or higher',
      });
    }
  }

  return results;
}
