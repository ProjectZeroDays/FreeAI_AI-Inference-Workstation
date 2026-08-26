import { detectFramework, findFiles, grepFiles, readText } from '../scanner.js';

export function diagnoseHydration(cwd) {
  const results = [];
  const { framework } = detectFramework(cwd);
  const jsFiles = findFiles(cwd, ['.js', '.jsx', '.ts', '.tsx']);

  // React / Next.js hydration issues
  if (framework === 'react' || framework === 'next') {
    // Check: window accessed during SSR without guard
    const windowAccess = grepFiles(jsFiles, /window\.\w+/);
    const windowGuards = grepFiles(jsFiles, /typeof\s+window\s*[!=]==?\s*['"]undefined['"]/);
    const useEffectWindow = grepFiles(jsFiles, /useEffect\s*\([\s\S]*?window/);
    if (windowAccess.length > 0 && windowGuards.length === 0 && useEffectWindow.length === 0) {
      results.push({
        rootCause: 'window accessed during SSR without guard — causes hydration mismatch',
        evidence: `${windowAccess[0].file}:${windowAccess[0].line} — ${windowAccess[0].text}`,
        fix: 'Wrap browser APIs in useEffect or guard with typeof window !== "undefined"',
      });
    }

    // Check: Date/Math.random in render — non-deterministic output
    const nonDeterministic = grepFiles(jsFiles, /new Date\(\)|Date\.now\(\)|Math\.random\(\)/);
    const filtered = nonDeterministic.filter(m =>
      !m.text.startsWith('//') && !m.text.startsWith('*') && !m.text.includes('useEffect')
    );
    if (filtered.length > 0) {
      results.push({
        rootCause: 'Non-deterministic value (Date/Math.random) in render — server/client mismatch',
        evidence: `${filtered[0].file}:${filtered[0].line} — ${filtered[0].text}`,
        fix: 'Move Date.now()/Math.random() into useEffect or pass as props from server',
      });
    }

    // Check: dangerouslySetInnerHTML with dynamic content
    const dangerousHtml = grepFiles(jsFiles, /dangerouslySetInnerHTML/);
    if (dangerousHtml.length > 0) {
      results.push({
        rootCause: 'dangerouslySetInnerHTML can cause hydration mismatch if content differs server/client',
        evidence: `${dangerousHtml[0].file}:${dangerousHtml[0].line} — ${dangerousHtml[0].text}`,
        fix: 'Ensure HTML string is identical on server and client, or use suppressHydrationWarning',
      });
    }

    // Check: Next.js — missing "use client" with hooks
    if (framework === 'next') {
      const hookFiles = grepFiles(jsFiles, /\b(useState|useEffect|useRef|useContext)\s*\(/);
      for (const match of hookFiles.slice(0, 5)) {
        const content = readText(match.file);
        if (content && !content.startsWith("'use client'") && !content.startsWith('"use client"')) {
          results.push({
            rootCause: 'React hook used in Next.js file without "use client" directive',
            evidence: `${match.file}:${match.line} — ${match.text}`,
            fix: 'Add "use client" at the top of the file, or move hook usage to a client component',
          });
          break;
        }
      }
    }
  }

  // Vue / Nuxt hydration issues
  if (framework === 'vue' || framework === 'nuxt') {
    const vueFiles = findFiles(cwd, ['.vue', '.js', '.ts']);

    // Check: document/window in setup or created
    const browserInSetup = grepFiles(vueFiles, /(setup|created)\s*\([\s\S]*?(document|window)\./);
    const directAccess = grepFiles(vueFiles, /^\s*(document|window)\.\w+/);
    if (browserInSetup.length > 0 || directAccess.length > 0) {
      const match = browserInSetup[0] || directAccess[0];
      results.push({
        rootCause: 'Browser API accessed during SSR in Vue — causes hydration mismatch',
        evidence: `${match.file}:${match.line} — ${match.text}`,
        fix: 'Use onMounted() or <ClientOnly> wrapper for browser-dependent code',
      });
    }

    // Check: v-html with dynamic content
    const vHtml = grepFiles(vueFiles, /v-html\s*=/);
    if (vHtml.length > 0) {
      results.push({
        rootCause: 'v-html can cause hydration mismatch if content differs server/client',
        evidence: `${vHtml[0].file}:${vHtml[0].line} — ${vHtml[0].text}`,
        fix: 'Ensure v-html content is identical on server and client, or wrap in <ClientOnly>',
      });
    }
  }

  return results;
}
