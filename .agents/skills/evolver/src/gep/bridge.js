const fs = require('fs');
const path = require('path');

function ensureDir(dir) {
  try {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  } catch (e) {}
}

function nowIso() {
  return new Date().toISOString();
}

function clip(text, maxChars) {
  const s = String(text || '');
  const n = Number(maxChars);
  if (!Number.isFinite(n) || n <= 0) return s;
  if (s.length <= n) return s;
  return s.slice(0, Math.max(0, n - 40)) + '\n...[TRUNCATED]...\n';
}

function writePromptArtifact({ memoryDir, cycleId, runId, prompt, meta }) {
  const dir = String(memoryDir || '').trim();
  if (!dir) throw new Error('bridge: missing memoryDir');
  ensureDir(dir);
  const safeCycle = String(cycleId || 'cycle').replace(/[^a-zA-Z0-9_\-#]/g, '_');
  const safeRun = String(runId || Date.now()).replace(/[^a-zA-Z0-9_\-]/g, '_');
  const base = `gep_prompt_${safeCycle}_${safeRun}`;
  const baseResolved = path.resolve(dir);
  const promptPath = path.resolve(baseResolved, base + '.txt');
  const metaPath = path.resolve(baseResolved, base + '.json');
  const promptRelative = path.relative(baseResolved, promptPath);
  const metaRelative = path.relative(baseResolved, metaPath);
  if (promptRelative.startsWith('..') || path.isAbsolute(promptRelative)) {
    throw new Error('bridge: invalid path');
  }
  if (metaRelative.startsWith('..') || path.isAbsolute(metaRelative)) {
    throw new Error('bridge: invalid path');
  }

  fs.writeFileSync(promptPath, String(prompt || ''), 'utf8');
  fs.writeFileSync(
    metaPath,
    JSON.stringify(
      {
        type: 'GepPromptArtifact',
        at: nowIso(),
        cycle_id: cycleId || null,
        run_id: runId || null,
        prompt_path: promptPath,
        meta: meta && typeof meta === 'object' ? meta : null,
      },
      null,
      2
    ) + '\n',
    'utf8'
  );

  return { promptPath, metaPath };
}

function renderSessionsSpawnCall({ task, agentId, label, cleanup }) {
  const t = String(task || '').trim();
  if (!t) throw new Error('bridge: missing task');
  const a = String(agentId || 'main');
  const l = String(label || 'gep_bridge');
  const c = cleanup ? String(cleanup) : 'delete';

  // Output valid JSON so wrappers can parse with JSON.parse (not regex).
  // The wrapper uses lastIndexOf('spawn_agent(') + JSON.parse to extract the task.
  const payload = JSON.stringify({ task: t, agentId: a, cleanup: c, label: l });
  return `spawn_agent(${payload})`;
}

module.exports = {
  clip,
  writePromptArtifact,
  renderSessionsSpawnCall,
};

