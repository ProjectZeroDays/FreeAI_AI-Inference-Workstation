export function formatReport(results) {
  if (!results.length) {
    console.log('\n  \x1b[32m✓ No issues detected.\x1b[0m\n');
    return;
  }
  for (const r of results) {
    console.log(`\n  \x1b[31m✗ Root Cause:\x1b[0m  ${r.rootCause}`);
    console.log(`    \x1b[33mEvidence:\x1b[0m    ${r.evidence}`);
    console.log(`    \x1b[36mFix:\x1b[0m         ${r.fix}`);
  }
  console.log();
}
