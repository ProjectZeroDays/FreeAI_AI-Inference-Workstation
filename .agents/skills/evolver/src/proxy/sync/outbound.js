'use strict';

const { PROXY_PROTOCOL_VERSION } = require('../mailbox/store');

const MAX_BATCH = 50;
const MAX_RETRIES = 10;

class OutboundSync {
  constructor({ store, hubUrl, getHeaders, logger }) {
    this.store = store;
    this.hubUrl = hubUrl;
    this.logger = logger || console;
    this.getHeaders = getHeaders;
  }

  async flush(channel = 'evomap-hub') {
    const pending = this.store.pollOutbound({ channel, limit: MAX_BATCH });
    if (pending.length === 0) return { sent: 0 };

    const endpoint = `${this.hubUrl}/a2a/mailbox/outbound`;

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          proxy_protocol_version: PROXY_PROTOCOL_VERSION,
          messages: pending.map(m => ({
            id: m.id,
            type: m.type,
            payload: m.payload,
            priority: m.priority,
            ref_id: m.ref_id,
            created_at: m.created_at,
          })),
        }),
        signal: AbortSignal.timeout(30_000),
      });

      if (!res.ok) {
        const errText = await res.text().catch(() => 'unknown');
        throw new Error(`Hub returned ${res.status}: ${errText}`);
      }

      const data = await res.json();
      const results = data.results || [];

      const updates = [];
      const inboundMessages = [];

      for (const r of results) {
        if (r.status === 'accepted' || r.status === 'ok') {
          updates.push({ id: r.id, status: 'synced' });
        } else if (r.status === 'failed' || r.status === 'rejected') {
          const msg = pending.find(m => m.id === r.id);
          if (msg && msg.retry_count < MAX_RETRIES) {
            this.store.incrementRetry(r.id, r.error || 'rejected by hub');
          } else {
            updates.push({ id: r.id, status: 'failed', error: r.error || 'max retries' });
          }
        }

        if (r.response) {
          inboundMessages.push({
            type: `${r.original_type || 'unknown'}_result`,
            payload: r.response,
            refId: r.id,
            channel,
          });
        }
      }

      if (updates.length > 0) this.store.updateStatusBatch(updates);
      if (inboundMessages.length > 0) this.store.writeInboundBatch(inboundMessages);

      this.store.setState('last_sync_at', new Date().toISOString());
      return { sent: pending.length, synced: updates.length, responses: inboundMessages.length };
    } catch (err) {
      this.logger.error(`[outbound] flush failed: ${err.message}`);
      for (const m of pending) {
        this.store.incrementRetry(m.id, err.message);
      }
      return { sent: 0, error: err.message };
    }
  }
}

module.exports = { OutboundSync, MAX_BATCH, MAX_RETRIES };
