'use strict';

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { MailboxStore } = require('../src/proxy/mailbox/store');
const { TaskMonitor } = require('../src/proxy/task/monitor');

function tmpDataDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'task-monitor-test-'));
}

describe('TaskMonitor', () => {
  let store, monitor, dataDir;

  before(() => {
    dataDir = tmpDataDir();
    store = new MailboxStore(dataDir);
    monitor = new TaskMonitor({ store });
  });

  after(() => {
    store.close();
    try { fs.rmSync(dataDir, { recursive: true }); } catch {}
  });

  describe('subscription', () => {
    it('is not subscribed initially', () => {
      assert.equal(monitor.subscribed, false);
    });

    it('subscribes and creates outbound message', () => {
      const result = monitor.subscribe(['code_review']);
      assert.ok(result.message_id);
      assert.equal(monitor.subscribed, true);
    });

    it('unsubscribes and creates outbound message', () => {
      const result = monitor.unsubscribe();
      assert.ok(result.message_id);
      assert.equal(monitor.subscribed, false);
    });

    it('persists subscription state', () => {
      monitor.subscribe(['testing']);
      const raw = store.getState('task_subscription');
      const parsed = JSON.parse(raw);
      assert.equal(parsed.enabled, true);
      assert.deepEqual(parsed.filters, ['testing']);
      assert.ok(parsed.subscribed_at);
      monitor.unsubscribe();
    });
  });

  describe('metrics tracking', () => {
    it('records claim', () => {
      monitor.recordClaim('task_1');
      const m = monitor.getMetrics();
      assert.equal(m.tasks_claimed, 1);
      assert.ok(m.last_claim_at);
    });

    it('records complete with duration', () => {
      const startedAt = Date.now() - 5000;
      monitor.recordComplete('task_1', startedAt);
      const m = monitor.getMetrics();
      assert.equal(m.tasks_completed, 1);
      assert.ok(m.last_complete_at);
      assert.ok(m.avg_completion_ms > 0);
    });

    it('records failed', () => {
      monitor.recordFailed('task_2');
      const m = monitor.getMetrics();
      assert.equal(m.tasks_failed, 1);
    });

    it('records tasks received', () => {
      monitor.recordTaskReceived(3);
      const m = monitor.getMetrics();
      assert.equal(m.tasks_received, 3);
    });

    it('accumulates metrics', () => {
      monitor.recordClaim('task_3');
      monitor.recordComplete('task_3', Date.now() - 2000);
      const m = monitor.getMetrics();
      assert.equal(m.tasks_claimed, 2);
      assert.equal(m.tasks_completed, 2);
    });
  });

  describe('getHeartbeatMeta', () => {
    it('returns structured meta for heartbeat', () => {
      monitor.subscribe([]);
      const meta = monitor.getHeartbeatMeta();
      assert.equal(meta.task_subscription, true);
      assert.ok('task_metrics' in meta);
      assert.equal(typeof meta.task_metrics.pending, 'number');
      assert.equal(typeof meta.task_metrics.claimed, 'number');
      assert.equal(typeof meta.task_metrics.completed, 'number');
      assert.equal(typeof meta.task_metrics.failed, 'number');
      assert.equal(typeof meta.task_metrics.avg_completion_ms, 'number');
      monitor.unsubscribe();
    });
  });

  describe('getMetrics', () => {
    it('includes pending tasks count', () => {
      const dir2 = tmpDataDir();
      const s2 = new MailboxStore(dir2);
      const m2 = new TaskMonitor({ store: s2 });
      s2.writeInbound({ type: 'task_available', payload: { task_id: 't1' } });
      s2.writeInbound({ type: 'task_available', payload: { task_id: 't2' } });
      const metrics = m2.getMetrics();
      assert.ok(metrics.tasks_pending >= 0);
      s2.close();
      try { fs.rmSync(dir2, { recursive: true }); } catch {}
    });
  });
});
