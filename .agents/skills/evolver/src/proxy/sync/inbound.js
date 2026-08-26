'use strict';

const { PROXY_PROTOCOL_VERSION } = require('../mailbox/store');

const DEFAULT_POLL_INTERVAL_ACTIVE = 10_000;
const DEFAULT_POLL_INTERVAL_IDLE = 60_000;

class InboundSync {
  constructor({ store, hubUrl, getHeaders, logger }) {
    this.store = store;
    this.hubUrl = hubUrl;
    this.logger = logger || console;
    this.getHeaders = getHeaders;
  }

  async pull(channel = 'evomap-hub', limit = 50) {
    const cursorKey = `${channel}:inbound_cursor`;
    const cursor = this.store.getCursor(cursorKey);

    const endpoint = `${this.hubUrl}/a2a/mailbox/inbound`;

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ proxy_protocol_version: PROXY_PROTOCOL_VERSION, cursor, limit }),
        signal: AbortSignal.timeout(35_000),
      });

      if (!res.ok) {
        const errText = await res.text().catch(() => 'unknown');
        throw new Error(`Hub returned ${res.status}: ${errText}`);
      }

      const data = await res.json();
      const messages = data.messages || [];

      if (messages.length > 0) {
        this.store.writeInboundBatch(
          messages.map(m => ({
            id: m.id,
            type: m.type,
            payload: m.payload,
            channel,
            priority: m.priority || 'normal',
            refId: m.ref_id,
            expiresAt: m.expires_at,
          }))
        );
      }

      if (data.next_cursor) {
        this.store.setCursor(cursorKey, data.next_cursor);
      }

      return { received: messages.length, cursor: data.next_cursor || cursor };
    } catch (err) {
      this.logger.error(`[inbound] pull failed: ${err.message}`);
      return { received: 0, error: err.message };
    }
  }

  async ackDelivered(channel = 'evomap-hub') {
    const delivered = this.store.list({
      type: '%',
      direction: 'inbound',
      status: 'delivered',
      limit: 100,
    }).filter(m => m.channel === channel);

    if (delivered.length === 0) return { acked: 0 };

    const endpoint = `${this.hubUrl}/a2a/mailbox/ack`;

    try {
      await fetch(endpoint, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ message_ids: delivered.map(m => m.id) }),
        signal: AbortSignal.timeout(10_000),
      });
      return { acked: delivered.length };
    } catch (err) {
      this.logger.error(`[inbound] ack failed: ${err.message}`);
      return { acked: 0, error: err.message };
    }
  }
}

module.exports = { InboundSync, DEFAULT_POLL_INTERVAL_ACTIVE, DEFAULT_POLL_INTERVAL_IDLE };
