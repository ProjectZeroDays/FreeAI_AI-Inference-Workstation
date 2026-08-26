'use strict';

class DmHandler {
  constructor({ store, logger } = {}) {
    this.store = store;
    this.logger = logger || console;
  }

  send({ recipientNodeId, content, metadata } = {}) {
    if (!recipientNodeId) throw new Error('recipientNodeId is required');
    if (!content) throw new Error('content is required');

    return this.store.send({
      type: 'dm',
      payload: {
        recipient_node_id: recipientNodeId,
        content,
        metadata: metadata || {},
        sent_at: new Date().toISOString(),
      },
      priority: 'normal',
    });
  }

  poll({ limit } = {}) {
    return this.store.poll({
      type: 'dm',
      limit: limit || 20,
    });
  }

  ack(messageIds) {
    return this.store.ack(messageIds);
  }

  list({ limit, offset } = {}) {
    return this.store.list({
      type: 'dm',
      limit: limit || 20,
      offset: offset || 0,
    });
  }
}

module.exports = { DmHandler };
