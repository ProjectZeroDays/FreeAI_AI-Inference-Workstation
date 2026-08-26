import { findFiles, grepFiles } from '../scanner.js';

export function diagnoseCssLayout(cwd) {
  const results = [];
  const cssFiles = findFiles(cwd, ['.css', '.scss', '.less']);
  const jsFiles = findFiles(cwd, ['.js', '.jsx', '.ts', '.tsx', '.vue']);
  const allStyleFiles = [...cssFiles, ...jsFiles];

  // Check: 100vh on mobile — doesn't account for browser chrome
  const vh100 = grepFiles(allStyleFiles, /100vh/);
  if (vh100.length > 0) {
    results.push({
      rootCause: '100vh used — overflows on mobile due to browser chrome',
      evidence: `${vh100[0].file}:${vh100[0].line} — ${vh100[0].text}`,
      fix: 'Use 100dvh (dynamic viewport height) or min-height: 100vh with overflow handling',
    });
  }

  // Check: overflow hidden on body — can break scroll
  const overflowBody = grepFiles(cssFiles, /body\s*\{[^}]*overflow\s*:\s*hidden/);
  if (overflowBody.length > 0) {
    results.push({
      rootCause: 'overflow: hidden on body — may prevent page scrolling',
      evidence: `${overflowBody[0].file}:${overflowBody[0].line} — ${overflowBody[0].text}`,
      fix: 'Remove overflow: hidden from body, or scope it to a modal-open state',
    });
  }

  // Check: z-index wars (very high values)
  const highZIndex = grepFiles(allStyleFiles, /z-index\s*:\s*(\d{4,})/);
  if (highZIndex.length > 3) {
    results.push({
      rootCause: 'Multiple high z-index values — likely z-index stacking issues',
      evidence: `${highZIndex.length} instances found, e.g. ${highZIndex[0].file}:${highZIndex[0].line}`,
      fix: 'Define a z-index scale (e.g. --z-dropdown: 100, --z-modal: 200) and use CSS custom properties',
    });
  }

  // Check: flex/grid without min-width: 0 — content overflow
  const flexContainers = grepFiles(allStyleFiles, /display\s*:\s*flex/);
  const minWidth0 = grepFiles(allStyleFiles, /min-width\s*:\s*0/);
  const textOverflow = grepFiles(allStyleFiles, /text-overflow\s*:\s*ellipsis/);
  if (flexContainers.length > 0 && textOverflow.length > 0 && minWidth0.length === 0) {
    results.push({
      rootCause: 'Flex layout with text-overflow but no min-width: 0 — text may overflow container',
      evidence: `${textOverflow[0].file}:${textOverflow[0].line} — ${textOverflow[0].text}`,
      fix: 'Add min-width: 0 to flex children that need text truncation',
    });
  }

  // Check: missing box-sizing border-box
  const boxSizing = grepFiles(cssFiles, /box-sizing\s*:\s*border-box/);
  const widthPercent = grepFiles(cssFiles, /width\s*:\s*\d+%/);
  const padding = grepFiles(cssFiles, /padding\s*:/);
  if (boxSizing.length === 0 && widthPercent.length > 0 && padding.length > 0) {
    results.push({
      rootCause: 'No box-sizing: border-box — percentage widths + padding will overflow',
      evidence: 'No box-sizing reset found in stylesheets',
      fix: 'Add *, *::before, *::after { box-sizing: border-box; } to your global styles',
    });
  }

  // Check: position fixed/sticky without width
  const fixedNoWidth = grepFiles(cssFiles, /position\s*:\s*(fixed|sticky)/);
  if (fixedNoWidth.length > 0) {
    const widthDecl = grepFiles(cssFiles, /position\s*:\s*(fixed|sticky)[^}]*width\s*:/);
    if (widthDecl.length === 0) {
      results.push({
        rootCause: 'position: fixed/sticky without explicit width — element may collapse or overflow',
        evidence: `${fixedNoWidth[0].file}:${fixedNoWidth[0].line} — ${fixedNoWidth[0].text}`,
        fix: 'Add width: 100% or explicit dimensions to fixed/sticky elements',
      });
    }
  }

  return results;
}
