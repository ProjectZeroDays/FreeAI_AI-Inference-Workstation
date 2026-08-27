'use strict';

const { PROXY_PROTOCOL_VERSION } = require('../mailbox/store');
const crypto = require('crypto');

const DEFAULT_HEARTBEAT_INTERVAL = 360_000;
const HELLO_TIMEOUT = 15_000;
const HEARTBEAT_TIMEOUT = 10_000;

class LifecycleManager {
  constructor({ hubUrl, store, logger, getTaskMeta } = {}) {
    this.hubUrl = (hubUrl || process.env.A2A_HUB_URL || '').replace(/\/+$/, '');
    this.store = store;
    this.logger = logger || console;
    this.getTaskMeta = getTaskMeta || null;
    this._heartbeatTimer = null;
    this._running = false;
    this._startedAt = null;
    this._consecutiveFailures = 0;
  }

  get nodeId() {
    return this.store.getState('node_id');
  }

  get nodeSecret() {
    return this.store.getState('node_secret') || process.env.A2A_NODE_SECRET || null;
  }

  _buildHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    const secret = this.nodeSecret;
    if (secret) headers['x-node-secret'] = secret;
    return headers;
  }

  async hello() {
    if (!this.hubUrl) return { ok: false, error: 'no_hub_url' };

    const endpoint = `${this.hubUrl}/a2a/hello`;
    const nodeId = this.store.getState('node_id') || `node_${crypto.randomBytes(6).toString('hex')}`;

    const body = {
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'hello',
      sender_id: nodeId,
      node_id: nodeId,
      capabilities: {},
      timestamp: new Date().toISOString(),
    };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: this._buildHeaders(),
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(HELLO_TIMEOUT),
      });
      const data = await res.json();

      const secret = data?.payload?.node_secret || data?.node_secret || null;
      if (secret && /^[a-f0-9]{64}$/i.test(secret)) {
        this.store.setState('node_secret', secret);
      }

      this.store.setState('node_id', nodeId);
      this.logger.log(`[lifecycle] hello OK, node_id=${nodeId}`);
      return { ok: true, nodeId, response: data };
    } catch (err) {
      this.logger.error(`[lifecycle] hello failed: ${err.message}`);
      return { ok: false, error: err.message };
    }
  }

  async heartbeat() {
    if (!this.hubUrl) return { ok: false, error: 'no_hub_url' };

    const nodeId = this.nodeId;
    if (!nodeId) {
      const helloResult = await this.hello();
      if (!helloResult.ok) return helloResult;
    }

    const endpoint = `${this.hubUrl}/a2a/heartbeat`;
    const body = {
      node_id: this.nodeId,
      sender_id: this.nodeId,
      version: '1.0.0',
      uptime_ms: this._startedAt ? Date.now() - this._startedAt : 0,
      timestamp: new Date().toISOString(),
      meta: {
        proxy_version: PROXY_PROTOCOL_VERSION,
        proxy_protocol_version: PROXY_PROTOCOL_VERSION,
        outbound_pending: this.store.countPending({ direction: 'outbound' }),
        inbound_pending: this.store.countPending({ direction: 'inbound' }),
        ...(typeof this.getTaskMeta === 'function' ? this.getTaskMeta() : {}),
      },
    };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: this._buildHeaders(),
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(HEARTBEAT_TIMEOUT),
      });
      const data = await res.json();

      this._consecutiveFailures = 0;
      this.store.setState('last_heartbeat_at', new Date().toISOString());

      if (data?.status === 'unknown_node') {
        this.logger.warn('[lifecycle] Node unknown, re-registering...');
        await this.hello();
      }

      if (Array.isArray(data?.events) && data.events.length > 0) {
        this.store.writeInboundBatch(
          data.events.map(e => ({
            type: e.type || 'hub_event',
            payload: e,
            channel: 'evomap-hub',
          }))
        );
      }

      if (data?.min_proxy_version && this._shouldUpgrade(data.min_proxy_version)) {
        this.store.writeInbound({
          type: 'system',
          payload: {
            action: 'proxy_upgrade_required',
            min_version: data.min_proxy_version,
            current_version: PROXY_PROTOCOL_VERSION,
            upgrade_url: data.upgrade_url || null,
            message: data.upgrade_message || 'Proxy version is below the minimum required by Hub.',
          },
          channel: 'evomap-hub',
          priority: 'high',
        });
        this.logger.warn(`[lifecycle] Hub requires proxy >= ${data.min_proxy_version}, current: ${PROXY_PROTOCOL_VERSION}`);
      }

      return { ok: true, response: data };
    } catch (err) {
      this._consecutiveFailures++;
      this.logger.error(`[lifecycle] heartbeat failed (${this._consecutiveFailures}): ${err.message}`);
      return { ok: false, error: err.message };
    }
  }

  startHeartbeatLoop(intervalMs) {
    if (this._running) return;
    this._running = true;
    this._startedAt = Date.now();

    const interval = Math.max(30_000, intervalMs || DEFAULT_HEARTBEAT_INTERVAL);

    const tick = async () => {
      if (!this._running) return;
      await this.heartbeat();
      if (this._running) {
        const backoff = this._consecutiveFailures > 0
          ? Math.min(interval * Math.pow(2, this._consecutiveFailures), 30 * 60_000)
          : interval;
        this._heartbeatTimer = setTimeout(tick, backoff);
        if (this._heartbeatTimer.unref) this._heartbeatTimer.unref();
      }
    };

    tick();
  }

  stopHeartbeatLoop() {
    this._running = false;
    if (this._heartbeatTimer) {
      clearTimeout(this._heartbeatTimer);
      this._heartbeatTimer = null;
    }
  }

  _shouldUpgrade(minVersion) {
    const parse = (v) => String(v || '0.0.0').split('.').map(Number);
    const min = parse(minVersion);
    const cur = parse(PROXY_PROTOCOL_VERSION);
    for (let i = 0; i < 3; i++) {
      if ((cur[i] || 0) < (min[i] || 0)) return true;
      if ((cur[i] || 0) > (min[i] || 0)) return false;
    }
    return false;
  }
}

module.exports = { LifecycleManager, DEFAULT_HEARTBEAT_INTERVAL };
