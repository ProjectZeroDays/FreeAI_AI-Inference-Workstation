'use strict';

class TaskMonitor {
  constructor({ store, logger } = {}) {
    this.store = store;
    this.logger = logger || console;
    this._stats = {
      tasks_received: 0,
      tasks_claimed: 0,
      tasks_completed: 0,
      tasks_failed: 0,
      last_claim_at: null,
      last_complete_at: null,
      avg_completion_ms: 0,
      _completion_times: [],
    };
    this._restoreStats();
  }

  _restoreStats() {
    const raw = this.store.getState('task_monitor_stats');
    if (!raw) return;
    try {
      const saved = typeof raw === 'string' ? JSON.parse(raw) : raw;
      if (saved.tasks_claimed) this._stats.tasks_claimed = saved.tasks_claimed;
      if (saved.tasks_completed) this._stats.tasks_completed = saved.tasks_completed;
      if (saved.tasks_failed) this._stats.tasks_failed = saved.tasks_failed;
      if (saved.tasks_received) this._stats.tasks_received = saved.tasks_received;
      if (saved.last_claim_at) this._stats.last_claim_at = saved.last_claim_at;
      if (saved.last_complete_at) this._stats.last_complete_at = saved.last_complete_at;
      if (saved.avg_completion_ms) this._stats.avg_completion_ms = saved.avg_completion_ms;
    } catch { /* ignore corrupt state */ }
  }

  get subscribed() {
    const raw = this.store.getState('task_subscription');
    if (!raw) return false;
    try {
      const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
      return !!parsed.enabled;
    } catch {
      return false;
    }
  }

  subscribe(filters = []) {
    this.store.setState('task_subscription', JSON.stringify({
      enabled: true,
      filters,
      subscribed_at: new Date().toISOString(),
    }));
    const result = this.store.send({
      type: 'task_subscribe',
      payload: { capability_filter: filters },
    });
    return result;
  }

  unsubscribe() {
    this.store.setState('task_subscription', JSON.stringify({
      enabled: false,
      unsubscribed_at: new Date().toISOString(),
    }));
    const result = this.store.send({
      type: 'task_unsubscribe',
      payload: {},
    });
    return result;
  }

  recordClaim(taskId) {
    this._stats.tasks_claimed++;
    this._stats.last_claim_at = Date.now();
    this.store.setState('task_monitor_stats', JSON.stringify(this.getMetrics()));
  }

  recordComplete(taskId, startedAt) {
    this._stats.tasks_completed++;
    this._stats.last_complete_at = Date.now();
    if (startedAt) {
      const duration = Date.now() - startedAt;
      this._stats._completion_times.push(duration);
      if (this._stats._completion_times.length > 100) {
        this._stats._completion_times.shift();
      }
      const sum = this._stats._completion_times.reduce((a, b) => a + b, 0);
      this._stats.avg_completion_ms = Math.round(sum / this._stats._completion_times.length);
    }
    this.store.setState('task_monitor_stats', JSON.stringify(this.getMetrics()));
  }

  recordFailed(taskId) {
    this._stats.tasks_failed++;
    this.store.setState('task_monitor_stats', JSON.stringify(this.getMetrics()));
  }

  recordTaskReceived(count = 1) {
    this._stats.tasks_received += count;
  }

  getMetrics() {
    const pendingTasks = this.store.countPending({ direction: 'inbound' });
    return {
      subscribed: this.subscribed,
      tasks_received: this._stats.tasks_received,
      tasks_claimed: this._stats.tasks_claimed,
      tasks_completed: this._stats.tasks_completed,
      tasks_failed: this._stats.tasks_failed,
      tasks_pending: pendingTasks,
      last_claim_at: this._stats.last_claim_at,
      last_complete_at: this._stats.last_complete_at,
      avg_completion_ms: this._stats.avg_completion_ms,
    };
  }

  getHeartbeatMeta() {
    const pendingTasks = this.store.countPending({ direction: 'inbound' });
    return {
      task_subscription: this.subscribed,
      task_metrics: {
        pending: pendingTasks,
        claimed: this._stats.tasks_claimed,
        completed: this._stats.tasks_completed,
        failed: this._stats.tasks_failed,
        avg_completion_ms: this._stats.avg_completion_ms,
      },
    };
  }
}

module.exports = { TaskMonitor };
