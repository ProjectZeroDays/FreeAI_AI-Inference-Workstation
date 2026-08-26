/**
 * Automated Deployment Script Template
 * Generates integration execution script for any component
 */

const fs = require('fs');
const path = require('path');

function createDeployScript(componentName, targetPaths) {
    return `#!/usr/bin/env node
/**
 * ${componentName}-integrator.js - Automated deployment
 */

const DEPLOY_BASE = process.cwd();

console.log('[$ {componentName}] Starting deployment...');

// Copy core files to target locations
${targetPaths.map((target, i) => `
// Target ${i+1}: ${target.dest}
if (!fs.existsSync('${target.dest}')) {
    fs.mkdirSync('${target.dest}', { recursive: true });
}
fs.copyFileSync(
    DEPLOY_BASE + '/${componentName}-integration/${target.src}',
    DEPLOY_BASE + '/${target.dest}/${target.src}'
);
console.log('[COPIED] ${componentName}/${target.src} -> ${target.dest}');
`).join('\n')}

console.log('[$ {componentName}] Deployment complete.');
`;
}

module.exports = { createDeployScript };