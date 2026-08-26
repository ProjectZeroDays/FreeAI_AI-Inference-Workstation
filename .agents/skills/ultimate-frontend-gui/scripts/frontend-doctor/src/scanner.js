import { readFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join, extname } from 'path';

export function readJson(filePath) {
  try {
    return JSON.parse(readFileSync(filePath, 'utf-8'));
  } catch {
    return null;
  }
}

export function readText(filePath) {
  try {
    return readFileSync(filePath, 'utf-8');
  } catch {
    return null;
  }
}

export function findFiles(dir, extensions, maxDepth = 4, depth = 0) {
  if (depth > maxDepth || !existsSync(dir)) return [];
  const results = [];
  try {
    for (const entry of readdirSync(dir)) {
      if (entry.startsWith('.') || entry === 'node_modules' || entry === 'dist' || entry === 'build') continue;
      const full = join(dir, entry);
      try {
        const stat = statSync(full);
        if (stat.isDirectory()) {
          results.push(...findFiles(full, extensions, maxDepth, depth + 1));
        } else if (extensions.includes(extname(entry))) {
          results.push(full);
        }
      } catch { /* skip inaccessible */ }
    }
  } catch { /* skip unreadable dir */ }
  return results;
}

export function detectFramework(cwd) {
  const pkg = readJson(join(cwd, 'package.json'));
  if (!pkg) return { framework: null, pkg: null };
  const deps = { ...pkg.dependencies, ...pkg.devDependencies };
  let framework = 'vanilla';
  if (deps['next']) framework = 'next';
  else if (deps['nuxt'] || deps['nuxt3']) framework = 'nuxt';
  else if (deps['react']) framework = 'react';
  else if (deps['vue']) framework = 'vue';
  else if (deps['svelte']) framework = 'svelte';
  let buildTool = null;
  if (deps['vite']) buildTool = 'vite';
  else if (deps['webpack']) buildTool = 'webpack';
  else if (deps['next']) buildTool = 'next';
  else if (deps['nuxt'] || deps['nuxt3']) buildTool = 'nuxt';
  return { framework, buildTool, pkg, deps };
}

export function grepFiles(files, pattern) {
  const matches = [];
  for (const file of files) {
    const content = readText(file);
    if (!content) continue;
    const lines = content.split('\n');
    for (let i = 0; i < lines.length; i++) {
      if (pattern.test(lines[i])) {
        matches.push({ file, line: i + 1, text: lines[i].trim() });
      }
    }
  }
  return matches;
}
