const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert');
const path = require('path');
const fs = require('fs');
const os = require('os');

const mg = require('../src/gep/memoryGraph');
const {
  selectGene, selectMultiGeneChunk, isInplaceGene,
  INPLACE_BLAST_MAX_FILES, INPLACE_BLAST_MAX_LINES,
} = require('../src/gep/selector');
const { buildInplaceGepPrompt } = require('../src/gep/prompt');

function setupTmpEnv() {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ttt-test-'));
  const origEnv = {};
  for (const k of ['EVOLVER_REPO_ROOT', 'MEMORY_GRAPH_PATH', 'EVOLUTION_DIR', 'OPENCLAW_WORKSPACE', 'EVOLVER_SESSION_SCOPE']) {
    origEnv[k] = process.env[k];
  }
  process.env.MEMORY_GRAPH_PATH = path.join(tmpDir, 'memory_graph.jsonl');
  process.env.EVOLUTION_DIR = tmpDir;
  delete process.env.OPENCLAW_WORKSPACE;
  delete process.env.EVOLVER_SESSION_SCOPE;
  return { tmpDir, origEnv };
}

function teardownTmpEnv(tmpDir, origEnv) {
  for (const [k, v] of Object.entries(origEnv)) {
    if (v !== undefined) process.env[k] = v;
    else delete process.env[k];
  }
  try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch (_) {}
}

// -- Phase 1: Predictive Outcome --

describe('Phase 1: computePredictiveBoost', () => {
  let tmpDir, origEnv;
  beforeEach(() => { ({ tmpDir, origEnv } = setupTmpEnv()); });
  afterEach(() => { teardownTmpEnv(tmpDir, origEnv); });

  it('returns positive boost for high-clarity actionable signals', () => {
    const result = mg.computePredictiveBoost({
      baselineObserved: { signal_count: 3 },
      currentObserved: {},
      signals: ['log_error', 'perf_bottleneck', 'capability_gap'],
    });
    assert.ok(result.boost > 0, `expected positive boost, got ${result.boost}`);
    assert.ok(result.signal_clarity > 0);
    assert.strictEqual(result.frontier_touched, false);
  });

  it('returns frontier_touched=true for curriculum signals', () => {
    const result = mg.computePredictiveBoost({
      baselineObserved: {},
      currentObserved: {},
      signals: ['curriculum_target:frontier:some_key', 'log_error'],
    });
    assert.strictEqual(result.frontier_touched, true);
    assert.ok(result.boost > 0);
  });

  it('handles empty signals gracefully', () => {
    const result = mg.computePredictiveBoost({
      baselineObserved: null,
      currentObserved: null,
      signals: [],
    });
    assert.strictEqual(typeof result.boost, 'number');
    assert.ok(result.boost >= -0.1 && result.boost <= 0.1);
  });

  it('reduces boost for decorative-only signals', () => {
    const allDecorative = mg.computePredictiveBoost({
      baselineObserved: {},
      currentObserved: {},
      signals: ['stable_success_plateau', 'memory_missing'],
    });
    const mixed = mg.computePredictiveBoost({
      baselineObserved: {},
      currentObserved: {},
      signals: ['stable_success_plateau', 'log_error'],
    });
    assert.ok(mixed.signal_clarity > allDecorative.signal_clarity);
  });
});

describe('Phase 1: inferOutcomeEnhanced with predictive', () => {
  let tmpDir, origEnv;
  beforeEach(() => { ({ tmpDir, origEnv } = setupTmpEnv()); });
  afterEach(() => { teardownTmpEnv(tmpDir, origEnv); });

  it('recordOutcomeFromState includes predictive field in outcome', () => {
    mg.recordAttempt({
      signals: ['log_error'],
      selectedGene: { id: 'gene_test', category: 'repair' },
      driftEnabled: false,
    });
    const ev = mg.recordOutcomeFromState({
      signals: ['stable_no_error'],
      observations: {},
    });
    assert.ok(ev);
    assert.strictEqual(ev.kind, 'outcome');
    assert.ok(ev.outcome.predictive, 'outcome should have predictive field');
    assert.strictEqual(typeof ev.outcome.predictive.signal_clarity, 'number');
    assert.strictEqual(typeof ev.outcome.predictive.frontier_touched, 'boolean');
  });
});

// -- Phase 2: In-Place Gene --

describe('Phase 2: isInplaceGene', () => {
  it('returns true for genes with execution_mode=inplace', () => {
    assert.strictEqual(isInplaceGene({ execution_mode: 'inplace' }), true);
  });

  it('returns false for regular genes', () => {
    assert.strictEqual(isInplaceGene({ type: 'Gene', id: 'gene_x' }), false);
  });

  it('returns falsy for null', () => {
    assert.ok(!isInplaceGene(null));
  });
});

describe('Phase 2: inplace gene preference in selectGene', () => {
  const GENES = [
    {
      type: 'Gene', id: 'gene_full', category: 'repair',
      signals_match: ['error', 'failed'],
      strategy: ['full fix'],
    },
    {
      type: 'Gene', id: 'gene_inplace', category: 'optimize',
      execution_mode: 'inplace',
      signals_match: ['error', 'timeout'],
      strategy: ['adjust timeout'],
    },
  ];

  it('prefers inplace gene when preferInplace=true and score is within threshold', () => {
    const orig = Math.random;
    Math.random = () => 0.99;
    try {
      const result = selectGene(GENES, ['error', 'timeout'], { preferInplace: true });
      assert.ok(result.selected);
      assert.strictEqual(result.selected.id, 'gene_inplace');
    } finally { Math.random = orig; }
  });

  it('does not force inplace when preferInplace=false', () => {
    const orig = Math.random;
    Math.random = () => 0.99;
    try {
      const result = selectGene(GENES, ['error', 'failed'], { preferInplace: false });
      assert.ok(result.selected);
      assert.strictEqual(result.selected.id, 'gene_full');
    } finally { Math.random = orig; }
  });
});

describe('Phase 2: buildInplaceGepPrompt', () => {
  it('produces a prompt with IN-PLACE MODE header', () => {
    const prompt = buildInplaceGepPrompt({
      nowIso: new Date().toISOString(),
      signals: ['timeout_error'],
      selectedGene: { id: 'gene_timeout_tune', strategy: ['Increase timeout to 30s'] },
      parentEventId: 'evt_123',
      cycleId: '42',
    });
    assert.ok(prompt.includes('IN-PLACE MODE'));
    assert.ok(prompt.includes('PARAMETER-ONLY'));
    assert.ok(prompt.includes('gene_timeout_tune'));
    assert.ok(prompt.includes('max 5 files'));
  });

  it('handles missing gene strategy gracefully', () => {
    const prompt = buildInplaceGepPrompt({
      signals: ['error'],
      selectedGene: { id: 'gene_x' },
    });
    assert.ok(prompt.includes('IN-PLACE MODE'));
    assert.ok(prompt.includes('Identify parameter'));
  });
});

describe('Phase 2: INPLACE constants', () => {
  it('exports blast radius limits', () => {
    assert.strictEqual(INPLACE_BLAST_MAX_FILES, 5);
    assert.strictEqual(INPLACE_BLAST_MAX_LINES, 100);
  });
});

// -- Phase 3: Multi-Gene Chunk --

describe('Phase 3: selectMultiGeneChunk', () => {
  const GENES = [
    {
      type: 'Gene', id: 'gene_error_fix', category: 'repair',
      signals_match: ['error', 'exception', 'failed'],
    },
    {
      type: 'Gene', id: 'gene_perf', category: 'optimize',
      signals_match: ['latency', 'throughput', 'slow'],
    },
    {
      type: 'Gene', id: 'gene_error_alt', category: 'repair',
      signals_match: ['error', 'crash', 'failed'],
    },
    {
      type: 'Gene', id: 'gene_innovate', category: 'innovate',
      signals_match: ['capability_gap', 'feature_request'],
    },
  ];

  it('returns primary gene when only one matches', () => {
    const result = selectMultiGeneChunk({
      genes: GENES,
      signals: ['capability_gap'],
      memoryAdvice: { bannedGeneIds: new Set(), preferredGeneId: null, totalAttempts: 0 },
      driftEnabled: false,
    });
    assert.ok(result.genes.length >= 1);
    assert.strictEqual(result.genes[0].id, 'gene_innovate');
  });

  it('selects multiple non-conflicting genes', () => {
    const result = selectMultiGeneChunk({
      genes: GENES,
      signals: ['error', 'latency', 'capability_gap'],
      memoryAdvice: { bannedGeneIds: new Set(), preferredGeneId: null, totalAttempts: 0 },
      driftEnabled: false,
    });
    assert.ok(result.genes.length >= 2, `expected >=2 genes, got ${result.genes.length}`);
    const ids = result.genes.map(g => g.id);
    assert.ok(!ids.includes('gene_error_alt') || !ids.includes('gene_error_fix'),
      'conflicting genes should not both be selected');
  });

  it('returns empty when no genes match', () => {
    const result = selectMultiGeneChunk({
      genes: GENES,
      signals: ['completely_unknown_signal'],
      memoryAdvice: null,
      driftEnabled: false,
    });
    assert.strictEqual(result.genes.length, 0);
  });
});

// -- Phase 4: Epoch Boundary & Memory Reset --

describe('Phase 4: checkEpochBoundary', () => {
  let tmpDir, origEnv;
  beforeEach(() => { ({ tmpDir, origEnv } = setupTmpEnv()); });
  afterEach(() => { teardownTmpEnv(tmpDir, origEnv); });

  it('triggers reset on consecutive_failure_streak_5 signal', () => {
    const result = mg.checkEpochBoundary({
      signals: ['consecutive_failure_streak_5', 'log_error'],
      currentEnvFingerprintKey: 'abc123',
      currentGeneLibVersion: 'glib_v1',
    });
    assert.strictEqual(result.shouldReset, true);
    assert.ok(result.reason.includes('consecutive_failure_streak_5'));
  });

  it('triggers reset on failure_loop_detected signal', () => {
    const result = mg.checkEpochBoundary({
      signals: ['failure_loop_detected'],
      currentEnvFingerprintKey: 'abc123',
      currentGeneLibVersion: 'glib_v1',
    });
    assert.strictEqual(result.shouldReset, true);
  });

  it('does not trigger reset for normal signals', () => {
    const result = mg.checkEpochBoundary({
      signals: ['log_error', 'perf_bottleneck'],
      currentEnvFingerprintKey: null,
      currentGeneLibVersion: null,
    });
    assert.strictEqual(result.shouldReset, false);
  });
});

describe('Phase 4: resetMemoryPreferences', () => {
  let tmpDir, origEnv;
  beforeEach(() => { ({ tmpDir, origEnv } = setupTmpEnv()); });
  afterEach(() => { teardownTmpEnv(tmpDir, origEnv); });

  it('writes epoch_boundary event and updates state', () => {
    const result = mg.resetMemoryPreferences({
      reason: 'env_major_change',
      currentEnvFingerprintKey: 'new_env_key',
      currentGeneLibVersion: 'glib_v2',
    });
    assert.ok(result.epochId);
    assert.strictEqual(result.reason, 'env_major_change');

    const graphPath = process.env.MEMORY_GRAPH_PATH;
    const lines = fs.readFileSync(graphPath, 'utf8').trim().split('\n');
    const epochEv = JSON.parse(lines[lines.length - 1]);
    assert.strictEqual(epochEv.kind, 'epoch_boundary');
    assert.strictEqual(epochEv.epoch.id, result.epochId);

    const epoch = mg.readCurrentEpoch();
    assert.strictEqual(epoch.epoch_id, result.epochId);
    assert.strictEqual(epoch.prev_env_fingerprint_key, 'new_env_key');
  });
});

describe('Phase 4: getMemoryAdvice with epoch filtering', () => {
  let tmpDir, origEnv;
  beforeEach(() => { ({ tmpDir, origEnv } = setupTmpEnv()); });
  afterEach(() => { teardownTmpEnv(tmpDir, origEnv); });

  it('deprioritizes pre-epoch outcomes after reset', () => {
    mg.recordAttempt({
      signals: ['error_a'],
      selectedGene: { id: 'gene_old', category: 'repair' },
      driftEnabled: false,
    });
    mg.recordOutcomeFromState({
      signals: ['stable_no_error'],
      observations: {},
    });

    mg.resetMemoryPreferences({
      reason: 'env_major_change',
      currentEnvFingerprintKey: 'new_key',
    });

    mg.recordAttempt({
      signals: ['error_a'],
      selectedGene: { id: 'gene_new', category: 'repair' },
      driftEnabled: false,
    });
    mg.recordOutcomeFromState({
      signals: ['stable_no_error'],
      observations: {},
    });

    const advice = mg.getMemoryAdvice({
      signals: ['error_a'],
      genes: [
        { id: 'gene_old', type: 'Gene' },
        { id: 'gene_new', type: 'Gene' },
      ],
      driftEnabled: false,
    });

    assert.ok(advice.preferredGeneId === 'gene_new' || advice.preferredGeneId === null,
      `after epoch reset, gene_new should be preferred over gene_old, got: ${advice.preferredGeneId}`);
  });
});
