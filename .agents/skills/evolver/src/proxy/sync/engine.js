'use strict';

const { OutboundSync } = require('./outbound');
const { InboundSync, DEFAULT_POLL_INTERVAL_ACTIVE, DEFAULT_POLL_INTERVAL_IDLE } = require('./inbound');

const DEFAULT_OUTBOUND_INTERVAL = 5_000;
const IDLE_THRESHOLD = 5 * 60_000;

class SyncEngine {
  constructor({ store, hubUrl, getHeaders, logger, onInboundReceived }) {
    this.store = store;
    this.hubUrl = hubUrl;
    this.logger = logger || console;
    this.getHeaders = getHeaders;
    this.onInboundReceived = onInboundReceived || null;

    this.outbound = new OutboundSync({ store, hubUrl, getHeaders, logger });
    this.inbound = new InboundSync({ store, hubUrl, getHeaders, logger });

    this._outTimer = null;
    this._inTimer = null;
    this._running = false;
    this._lastActivity = Date.now();
  }

  start() {
    if (this._running) return;
    this._running = true;
    this._lastActivity = Date.now();
    this._scheduleOutbound(500);
    this._scheduleInbound(1_000);
    this.logger.log('[sync] engine started');
  }

  stop() {
    this._running = false;
    if (this._outTimer) { clearTimeout(this._outTimer); this._outTimer = null; }
    if (this._inTimer) { clearTimeout(this._inTimer); this._inTimer = null; }
    this.logger.log('[sync] engine stopped');
  }

  notifyNewOutbound() {
    this._lastActivity = Date.now();
    if (this._running && !this._outPending) {
      if (this._outTimer) clearTimeout(this._outTimer);
      this._scheduleOutbound(100);
    }
  }

  _isIdle() {
    return (Date.now() - this._lastActivity) > IDLE_THRESHOLD;
  }

  _scheduleOutbound(delayMs) {
    if (!this._running) return;
    this._outTimer = setTimeout(async () => {
      if (!this._running) return;
      this._outPending = true;
      try {
        const result = await this.outbound.flush();
        if (result.sent > 0) this._lastActivity = Date.now();
      } catch (err) {
        this.logger.error(`[sync] outbound error: ${err.message}`);
      }
      this._outPending = false;
      const nextDelay = this.store.countPending({ direction: 'outbound' }) > 0
        ? 1_000
        : DEFAULT_OUTBOUND_INTERVAL;
      this._scheduleOutbound(nextDelay);
    }, delayMs);
    if (this._outTimer.unref) this._outTimer.unref();
  }

  _scheduleInbound(delayMs) {
    if (!this._running) return;
    this._inTimer = setTimeout(async () => {
      if (!this._running) return;
      try {
        const result = await this.inbound.pull();
        if (result.received > 0) {
          this._lastActivity = Date.now();
          if (typeof this.onInboundReceived === 'function') {
            try { this.onInboundReceived(result.received); } catch {}
          }
        }
        await this.inbound.ackDelivered();
      } catch (err) {
        this.logger.error(`[sync] inbound error: ${err.message}`);
      }
      const nextDelay = this._isIdle()
        ? DEFAULT_POLL_INTERVAL_IDLE
        : DEFAULT_POLL_INTERVAL_ACTIVE;
      this._scheduleInbound(nextDelay);
    }, delayMs);
    if (this._inTimer.unref) this._inTimer.unref();
  }
}

module.exports = { SyncEngine, DEFAULT_OUTBOUND_INTERVAL };
