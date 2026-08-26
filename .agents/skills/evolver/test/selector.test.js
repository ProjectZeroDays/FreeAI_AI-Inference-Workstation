const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { selectGene, selectCapsule, selectGeneAndCapsule } = require('../src/gep/selector');

const GENES = [
  {
    type: 'Gene',
    id: 'gene_repair',
    category: 'repair',
    signals_match: ['error', 'exception', 'failed'],
    strategy: ['fix it'],
    validation: ['node -e "true"'],
  },
  {
    type: 'Gene',
    id: 'gene_optimize',
    category: 'optimize',
    signals_match: ['protocol', 'prompt', 'audit'],
    strategy: ['optimize it'],
    validation: ['node -e "true"'],
  },
  {
    type: 'Gene',
    id: 'gene_innovate',
    category: 'innovate',
    signals_match: ['user_feature_request', 'user_improvement_suggestion', 'capability_gap', 'stable_success_plateau'],
    strategy: ['build it'],
    validation: ['node -e "true"'],
  },
  {
    type: 'Gene',
    id: 'gene_perf_optimize',
    category: 'optimize',
    signals_match: ['latency', 'throughput'],
    summary: 'Reduce latency and improve throughput on slow paths',
    strategy: ['speed it up'],
    validation: ['node -e "true"'],
  },
];

const CAPSULES = [
  {
    type: 'Capsule',
    id: 'capsule_1',
    trigger: ['log_error', 'exception'],
    gene: 'gene_repair',
    summary: 'Fixed an error',
    confidence: 0.9,
  },
  {
    type: 'Capsule',
    id: 'capsule_2',
    trigger: ['protocol', 'gep'],
    gene: 'gene_optimize',
    summary: 'Optimized prompt',
    confidence: 0.85,
  },
];

describe('selectGene', () => {
  it('selects the gene with highest signal match', () => {
    const result = selectGene(GENES, ['error', 'exception', 'failed'], {});
    assert.equal(result.selected.id, 'gene_repair');
  });

  it('returns null when no signals match', () => {
    const result = selectGene(GENES, ['completely_unrelated_signal'], {});
    assert.equal(result.selected, null);
  });

  it('returns alternatives when multiple genes match', () => {
    const result = selectGene(GENES, ['error', 'protocol'], {});
    assert.ok(result.selected);
    assert.ok(Array.isArray(result.alternatives));
  });

  it('includes drift intensity in result', () => {
    // Drift intensity is population-size-dependent; verify it is returned.
    const result = selectGene(GENES, ['error', 'exception'], {});
    assert.ok('driftIntensity' in result);
    assert.equal(typeof result.driftIntensity, 'number');
    assert.ok(result.driftIntensity >= 0 && result.driftIntensity <= 1);
  });

  it('applies score multiplier for preferred gene from memory graph', () => {
    const orig = Math.random;
    Math.random = () => 0.99;
    try {
      const result = selectGene(GENES, ['error', 'protocol'], {
        preferredGeneId: 'gene_optimize',
      });
      assert.equal(result.selected.id, 'gene_optimize');
    } finally { Math.random = orig; }
  });

  it('does not let multiplier override a much-higher-scoring gene', () => {
    const orig = Math.random;
    Math.random = () => 0.99;
    try {
      const result = selectGene(GENES, ['error', 'exception', 'failed'], {
        preferredGeneId: 'gene_optimize',
      });
      assert.equal(result.selected.id, 'gene_repair');
    } finally { Math.random = orig; }
  });

  it('matches gene via baseName:snippet signal (user_feature_request:snippet)', () => {
    const result = selectGene(GENES, ['user_feature_request:add a dark mode toggle to the settings'], {});
    assert.ok(result.selected);
    assert.equal(result.selected.id, 'gene_innovate', 'innovate gene has signals_match user_feature_request');
  });

  it('matches gene via baseName:snippet signal (user_improvement_suggestion:snippet)', () => {
    const result = selectGene(GENES, ['user_improvement_suggestion:refactor the payment module and simplify the API'], {});
    assert.ok(result.selected);
    assert.equal(result.selected.id, 'gene_innovate', 'innovate gene has signals_match user_improvement_suggestion');
  });

  it('uses derived learning tags to match related performance genes', () => {
    const originalRandom = Math.random;
    Math.random = () => 0.99;
    try {
      const result = selectGene(GENES, ['perf_bottleneck'], { effectivePopulationSize: 100 });
      assert.ok(result.selected);
      assert.equal(result.selected.id, 'gene_perf_optimize');
    } finally {
      Math.random = originalRandom;
    }
  });

  it('downweights genes with repeated hard-fail anti-patterns', () => {
    const originalRandom = Math.random;
    Math.random = () => 0.99;
    try {
      const riskyGenes = [
        {
          type: 'Gene',
          id: 'gene_perf_risky',
          category: 'optimize',
          signals_match: ['perf_bottleneck'],
          anti_patterns: [
            { mode: 'hard', learning_signals: ['problem:performance'] },
            { mode: 'hard', learning_signals: ['problem:performance'] },
          ],
          validation: ['node -e "true"'],
        },
        {
          type: 'Gene',
          id: 'gene_perf_safe',
          category: 'optimize',
          signals_match: ['perf_bottleneck'],
          learning_history: [
            { outcome: 'success', mode: 'none' },
          ],
          validation: ['node -e "true"'],
        },
      ];
      const result = selectGene(riskyGenes, ['perf_bottleneck'], { effectivePopulationSize: 100 });
      assert.ok(result.selected);
      assert.equal(result.selected.id, 'gene_perf_safe');
    } finally {
      Math.random = originalRandom;
    }
  });
});

describe('selectCapsule', () => {
  it('selects capsule matching signals', () => {
    const result = selectCapsule(CAPSULES, ['log_error', 'exception']);
    assert.equal(result.id, 'capsule_1');
  });

  it('returns null when no triggers match', () => {
    const result = selectCapsule(CAPSULES, ['unrelated']);
    assert.equal(result, null);
  });
});

describe('selectGeneAndCapsule', () => {
  it('returns selected gene, capsule candidates, and selector decision', () => {
    const result = selectGeneAndCapsule({
      genes: GENES,
      capsules: CAPSULES,
      signals: ['error', 'log_error'],
      memoryAdvice: null,
      driftEnabled: false,
    });
    assert.ok(result.selectedGene);
    assert.ok(result.selector);
    assert.ok(result.selector.selected);
    assert.ok(Array.isArray(result.selector.reason));
  });

  it('includes selectionPath and memoryUsed telemetry', () => {
    const result = selectGeneAndCapsule({
      genes: GENES,
      capsules: CAPSULES,
      signals: ['error', 'log_error'],
      memoryAdvice: { bannedGeneIds: new Set(), preferredGeneId: null, totalAttempts: 0 },
      driftEnabled: false,
    });
    assert.ok(result.selectionPath);
    assert.equal(typeof result.memoryUsed, 'boolean');
    assert.equal(typeof result.memoryEvidence, 'number');
    assert.ok(result.selector.selectionPath);
  });
});

describe('computeDriftIntensity adaptive decay', () => {
  const { computeDriftIntensity } = require('../src/gep/selector');

  it('returns base drift with max offset when no memory evidence', () => {
    const d = computeDriftIntensity({ driftEnabled: true, genePoolSize: 10, memoryEvidence: 0 });
    const expected = Math.min(1, 1 / Math.sqrt(10) + 0.3);
    assert.ok(Math.abs(d - expected) < 0.001, `expected ~${expected.toFixed(3)}, got ${d.toFixed(3)}`);
  });

  it('decays offset as memory evidence grows', () => {
    const dLow = computeDriftIntensity({ driftEnabled: true, genePoolSize: 10, memoryEvidence: 0 });
    const dMid = computeDriftIntensity({ driftEnabled: true, genePoolSize: 10, memoryEvidence: 50 });
    const dHigh = computeDriftIntensity({ driftEnabled: true, genePoolSize: 10, memoryEvidence: 200 });
    assert.ok(dLow > dMid, `low evidence drift ${dLow} should exceed mid ${dMid}`);
    assert.ok(dMid > dHigh, `mid evidence drift ${dMid} should exceed high ${dHigh}`);
  });

  it('reaches floor offset at full maturity', () => {
    const ne = 10;
    const fullMature = ne * 10;
    const d = computeDriftIntensity({ driftEnabled: true, genePoolSize: ne, memoryEvidence: fullMature * 2 });
    const expectedFloor = Math.min(1, 1 / Math.sqrt(ne) + 0.02);
    assert.ok(Math.abs(d - expectedFloor) < 0.001, `expected floor ~${expectedFloor.toFixed(3)}, got ${d.toFixed(3)}`);
  });

  it('returns population-dependent drift when not explicitly enabled', () => {
    const d = computeDriftIntensity({ driftEnabled: false, genePoolSize: 10, memoryEvidence: 50 });
    const expected = Math.min(1, 1 / Math.sqrt(10));
    assert.ok(Math.abs(d - expected) < 0.001, `expected ~${expected.toFixed(3)}, got ${d.toFixed(3)}`);
  });
});
