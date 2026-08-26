'use strict';

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { getEvolutionDir, getRepoRoot } = require('./paths');

const EXPLORE_ENABLED = String(process.env.EVOLVER_EXPLORE_ENABLED || 'true').toLowerCase() !== 'false';
const EXPLORE_COOLDOWN_MS = parseInt(process.env.EVOLVER_EXPLORE_COOLDOWN_MS || '1800000', 10) || 1800000;
const ARXIV_CATEGORIES = (process.env.EVOLVER_EXPLORE_ARXIV_CATEGORIES || 'cs.AI,cs.SE').split(',').map(s => s.trim()).filter(Boolean);
const STALE_DAYS = parseInt(process.env.EVOLVER_EXPLORE_STALE_DAYS || '30', 10) || 30;

const MAX_INTERNAL_RESULTS = 20;
const MAX_EXTERNAL_RESULTS = 10;
const LARGE_FILE_LINES = 500;

function _getExploreStatePath() {
  return path.join(getEvolutionDir(), 'explore_status.json');
}

function readExploreState() {
  try {
    const raw = fs.readFileSync(_getExploreStatePath(), 'utf8');
    return JSON.parse(raw);
  } catch (_) {
    return {};
  }
}

function writeExploreState(results) {
  const dir = getEvolutionDir();
  const statePath = _getExploreStatePath();
  try {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const state = {
      last_explore_at: new Date().toISOString(),
      last_explore_ts: Date.now(),
      result_count: results.length,
      results: results.slice(0, 30),
    };
    const tmp = statePath + '.tmp';
    fs.writeFileSync(tmp, JSON.stringify(state, null, 2) + '\n', 'utf8');
    fs.renameSync(tmp, statePath);
  } catch (_) {}
}

function shouldExplore(signals, schedule) {
  if (!EXPLORE_ENABLED) return false;

  if (schedule && schedule.should_explore) {
    const state = readExploreState();
    const lastTs = state.last_explore_ts || 0;
    if (Date.now() - lastTs < EXPLORE_COOLDOWN_MS) return false;
    return true;
  }

  const sigList = Array.isArray(signals) ? signals : [];
  if (sigList.includes('explore_opportunity')) {
    const state = readExploreState();
    const lastTs = state.last_explore_ts || 0;
    if (Date.now() - lastTs < EXPLORE_COOLDOWN_MS) return false;
    return true;
  }

  return false;
}

function exploreInternal(repoDir) {
  const results = [];
  const root = repoDir || getRepoRoot();

  _scanTodoComments(root, results);
  _scanStaleFiles(root, results);
  _scanLargeFiles(root, results);

  return results.slice(0, MAX_INTERNAL_RESULTS);
}

function _isIgnored(rel) {
  return /node_modules|\.git\/|dist\/|build\/|\.min\.js|package-lock|\.lock$|\.map$/.test(rel);
}

function _isSourceFile(name) {
  return /\.(js|ts|py|mjs|cjs|jsx|tsx)$/.test(name);
}

function _scanTodoComments(root, results) {
  try {
    const cmd = 'grep -rn --include="*.js" --include="*.ts" --include="*.py" ' +
      '-E "(TODO|FIXME|HACK|XXX)\\b" . 2>/dev/null | head -50';
    const out = execSync(cmd, { cwd: root, timeout: 10000, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
    const lines = out.split('\n').filter(Boolean);
    const seen = new Set();
    for (const line of lines) {
      const match = line.match(/^\.\/(.+?):(\d+):\s*(.*)$/);
      if (!match) continue;
      const [, filePath, lineNum, content] = match;
      if (_isIgnored(filePath)) continue;
      const key = filePath + ':' + lineNum;
      if (seen.has(key)) continue;
      seen.add(key);
      const tag = (content.match(/\b(TODO|FIXME|HACK|XXX)\b/i) || ['TODO'])[0].toUpperCase();
      results.push({
        type: 'internal',
        category: 'todo_comment',
        tag,
        file: filePath,
        line: parseInt(lineNum, 10),
        snippet: content.trim().slice(0, 200),
      });
    }
  } catch (_) {}
}

function _scanStaleFiles(root, results) {
  const thresholdMs = STALE_DAYS * 24 * 60 * 60 * 1000;
  const now = Date.now();
  try {
    const cmd = `find . -type f \\( -name "*.js" -o -name "*.ts" -o -name "*.py" \\) ` +
      `-not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" ` +
      `-mtime +${STALE_DAYS} 2>/dev/null | head -30`;
    const out = execSync(cmd, { cwd: root, timeout: 10000, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
    const files = out.split('\n').filter(Boolean);
    for (const f of files) {
      const rel = f.replace(/^\.\//, '');
      if (_isIgnored(rel)) continue;
      try {
        const stat = fs.statSync(path.join(root, rel));
        const ageDays = Math.floor((now - stat.mtimeMs) / (24 * 60 * 60 * 1000));
        results.push({
          type: 'internal',
          category: 'stale_file',
          file: rel,
          age_days: ageDays,
          size_bytes: stat.size,
        });
      } catch (_) {}
    }
  } catch (_) {}
}

function _scanLargeFiles(root, results) {
  try {
    const cmd = `find . -type f \\( -name "*.js" -o -name "*.ts" \\) ` +
      `-not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" ` +
      `-exec wc -l {} + 2>/dev/null | sort -rn | head -15`;
    const out = execSync(cmd, { cwd: root, timeout: 10000, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
    const lines = out.split('\n').filter(Boolean);
    for (const line of lines) {
      const match = line.match(/^\s*(\d+)\s+(.+)$/);
      if (!match) continue;
      const [, countStr, filePath] = match;
      const count = parseInt(countStr, 10);
      if (count < LARGE_FILE_LINES) continue;
      const rel = filePath.replace(/^\.\//, '');
      if (_isIgnored(rel) || rel === 'total') continue;
      results.push({
        type: 'internal',
        category: 'large_file',
        file: rel,
        lines: count,
      });
    }
  } catch (_) {}
}

async function exploreExternal(signals) {
  const results = [];

  await _searchHub(signals, results);
  await _searchArxiv(results);

  return results.slice(0, MAX_EXTERNAL_RESULTS);
}

async function _searchHub(signals, results) {
  try {
    const { hubSearch } = require('./hubSearch');
    const hit = await hubSearch(signals, { timeoutMs: 5000 });
    if (hit && hit.hit && hit.match) {
      results.push({
        type: 'external',
        category: 'hub_asset',
        asset_id: hit.asset_id || hit.match.asset_id,
        score: hit.score,
        mode: hit.mode,
        name: hit.match.name || hit.match.asset_id || 'unknown',
      });
    }
  } catch (_) {}
}

async function _searchArxiv(results) {
  for (const cat of ARXIV_CATEGORIES.slice(0, 3)) {
    try {
      const url = `http://export.arxiv.org/api/query?search_query=cat:${encodeURIComponent(cat)}&max_results=3&sortBy=submittedDate&sortOrder=descending`;
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 8000);
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timer);
      if (!res.ok) continue;
      const xml = await res.text();
      const entries = xml.split('<entry>').slice(1);
      for (const entry of entries.slice(0, 3)) {
        const title = _xmlTag(entry, 'title').replace(/\s+/g, ' ').trim();
        const summary = _xmlTag(entry, 'summary').replace(/\s+/g, ' ').trim().slice(0, 300);
        const id = _xmlTag(entry, 'id');
        if (!title) continue;
        results.push({
          type: 'external',
          category: 'arxiv_paper',
          arxiv_category: cat,
          title,
          summary,
          url: id,
        });
      }
    } catch (_) {}
  }
}

function _xmlTag(xml, tag) {
  const re = new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, 'i');
  const m = xml.match(re);
  return m ? m[1].trim() : '';
}

function convertToSignals(results) {
  const signals = [];
  const seen = new Set();
  for (const r of results) {
    let sig;
    if (r.type === 'internal') {
      sig = `explore:internal:${r.category}`;
    } else {
      sig = `explore:external:${r.category}`;
    }
    if (!seen.has(sig)) {
      seen.add(sig);
      signals.push(sig);
    }
  }
  if (signals.length > 0 && !signals.includes('explore_opportunity')) {
    signals.unshift('explore_opportunity');
  }
  return signals;
}

async function tryExplore(signals, schedule, repoDir) {
  if (!shouldExplore(signals, schedule)) return { items: [], signals: [] };

  console.log('[Explore] Entering exploration mode...');
  const t0 = Date.now();

  const internal = exploreInternal(repoDir);
  const external = await exploreExternal(signals);
  const all = [...internal, ...external];

  let injected = [];
  if (all.length > 0) {
    writeExploreState(all);
    injected = convertToSignals(all);
    console.log(`[Explore] Found ${all.length} items (${internal.length} internal, ${external.length} external) in ${Date.now() - t0}ms. Injected signals: ${injected.join(', ')}`);
  } else {
    console.log(`[Explore] No findings in ${Date.now() - t0}ms.`);
  }

  return { items: all, signals: injected };
}

module.exports = {
  shouldExplore,
  exploreInternal,
  exploreExternal,
  convertToSignals,
  writeExploreState,
  readExploreState,
  tryExplore,
};
