'use strict';

const { PROXY_PROTOCOL_VERSION, SCHEMA_VERSION } = require('../mailbox/store');

function buildRoutes(store, proxyHandlers, taskMonitor, extensions) {
  const { dmHandler, skillUpdater, getHubMailboxStatus } = extensions || {};
  return {
    // -- Mailbox --
    'POST /mailbox/send': async ({ body }) => {
      if (!body.type) throw Object.assign(new Error('type is required'), { statusCode: 400 });
      if (!body.payload) throw Object.assign(new Error('payload is required'), { statusCode: 400 });
      const result = store.send({
        type: body.type,
        payload: body.payload,
        channel: body.channel,
        priority: body.priority,
        refId: body.ref_id,
        expiresAt: body.expires_at,
      });
      return { body: result };
    },

    'POST /mailbox/poll': async ({ body }) => {
      const messages = store.poll({
        channel: body.channel,
        type: body.type,
        limit: body.limit,
      });
      return { body: { messages, count: messages.length } };
    },

    'POST /mailbox/ack': async ({ body }) => {
      if (!body.message_ids) throw Object.assign(new Error('message_ids is required'), { statusCode: 400 });
      const count = store.ack(body.message_ids);
      return { body: { acknowledged: count } };
    },

    'GET /mailbox/list': async ({ query }) => {
      if (!query.type) throw Object.assign(new Error('type query param is required'), { statusCode: 400 });
      const messages = store.list({
        type: query.type,
        direction: query.direction,
        status: query.status,
        limit: Number(query.limit) || 20,
        offset: Number(query.offset) || 0,
      });
      return { body: { messages, count: messages.length } };
    },

    'GET /mailbox/status/:id': async ({ params }) => {
      const msg = store.getById(params.id);
      if (!msg) throw Object.assign(new Error('Message not found'), { statusCode: 404 });
      return { body: msg };
    },

    // -- Asset (proxy HTTP) --
    'POST /asset/validate': async ({ body }) => {
      if (!body.asset_id && !body.assets) {
        throw Object.assign(new Error('asset_id or assets is required'), { statusCode: 400 });
      }
      const result = await proxyHandlers.assetValidate(body);
      return { body: result };
    },

    'POST /asset/fetch': async ({ body }) => {
      const result = await proxyHandlers.assetFetch(body);
      return { body: result };
    },

    'POST /asset/search': async ({ body }) => {
      const result = await proxyHandlers.assetSearch(body);
      return { body: result };
    },

    'POST /asset/submit': async ({ body }) => {
      if (!body.assets && !body.asset_id) {
        throw Object.assign(new Error('assets or asset_id is required'), { statusCode: 400 });
      }
      const result = store.send({
        type: 'asset_submit',
        payload: body,
        priority: body.priority || 'normal',
      });
      return { body: result };
    },

    'GET /asset/submissions': async ({ query }) => {
      const submissions = store.list({
        type: 'asset_submit',
        direction: 'outbound',
        status: query.status || undefined,
        limit: Number(query.limit) || 20,
        offset: Number(query.offset) || 0,
      });
      const submissionIds = new Set(submissions.map(s => s.id));
      const resultMap = {};
      for (const [, msg] of store._messages) {
        if (msg.type !== 'asset_submit_result' || msg.direction !== 'inbound') continue;
        const refId = msg.payload?.ref_id;
        if (refId && submissionIds.has(refId)) resultMap[refId] = msg;
      }
      const enriched = submissions.map(s => ({
        ...s,
        result: resultMap[s.id] ? { ...resultMap[s.id] } : null,
      }));
      return { body: { submissions: enriched, count: enriched.length } };
    },

    // -- Task --
    'POST /task/subscribe': async ({ body }) => {
      if (taskMonitor) {
        const result = taskMonitor.subscribe(body.capability_filter || body.filters || []);
        return { body: result };
      }
      const result = store.send({
        type: 'task_subscribe',
        payload: body || {},
      });
      return { body: result };
    },

    'POST /task/unsubscribe': async ({ body }) => {
      if (taskMonitor) {
        const result = taskMonitor.unsubscribe();
        return { body: result };
      }
      const result = store.send({
        type: 'task_unsubscribe',
        payload: body || {},
      });
      return { body: result };
    },

    'GET /task/list': async ({ query }) => {
      const messages = store.poll({
        type: 'task_available',
        limit: Number(query.limit) || 20,
      });
      return { body: { tasks: messages, count: messages.length } };
    },

    'POST /task/claim': async ({ body }) => {
      if (!body.task_id) throw Object.assign(new Error('task_id is required'), { statusCode: 400 });
      const result = store.send({
        type: 'task_claim',
        payload: body,
        priority: 'high',
      });
      if (taskMonitor) taskMonitor.recordClaim(body.task_id);
      return { body: result };
    },

    'POST /task/complete': async ({ body }) => {
      if (!body.task_id) throw Object.assign(new Error('task_id is required'), { statusCode: 400 });
      const result = store.send({
        type: 'task_complete',
        payload: body,
      });
      if (taskMonitor) taskMonitor.recordComplete(body.task_id, body.started_at);
      return { body: result };
    },

    'GET /task/metrics': async () => {
      if (!taskMonitor) {
        return { body: { subscribed: false, metrics: null } };
      }
      return { body: taskMonitor.getMetrics() };
    },

    // -- DM (Direct Message) --
    'POST /dm/send': async ({ body }) => {
      if (!body.recipient_node_id) {
        throw Object.assign(new Error('recipient_node_id is required'), { statusCode: 400 });
      }
      if (!body.content) {
        throw Object.assign(new Error('content is required'), { statusCode: 400 });
      }
      if (dmHandler) {
        const result = dmHandler.send({
          recipientNodeId: body.recipient_node_id,
          content: body.content,
          metadata: body.metadata,
        });
        return { body: result };
      }
      const result = store.send({
        type: 'dm',
        payload: {
          recipient_node_id: body.recipient_node_id,
          content: body.content,
          metadata: body.metadata || {},
        },
      });
      return { body: result };
    },

    'POST /dm/poll': async ({ body }) => {
      if (dmHandler) {
        const messages = dmHandler.poll({ limit: body.limit });
        return { body: { messages, count: messages.length } };
      }
      const messages = store.poll({ type: 'dm', limit: body.limit || 20 });
      return { body: { messages, count: messages.length } };
    },

    'GET /dm/list': async ({ query }) => {
      if (dmHandler) {
        const messages = dmHandler.list({
          limit: Number(query.limit) || 20,
          offset: Number(query.offset) || 0,
        });
        return { body: { messages, count: messages.length } };
      }
      const messages = store.list({
        type: 'dm',
        limit: Number(query.limit) || 20,
        offset: Number(query.offset) || 0,
      });
      return { body: { messages, count: messages.length } };
    },

    // -- System --
    'GET /proxy/status': async () => {
      const outPending = store.countPending({ direction: 'outbound' });
      const inPending = store.countPending({ direction: 'inbound' });
      const nodeId = store.getState('node_id');
      const lastSync = store.getState('last_sync_at');
      return {
        body: {
          status: 'running',
          node_id: nodeId,
          proxy_protocol_version: PROXY_PROTOCOL_VERSION,
          schema_version: SCHEMA_VERSION,
          outbound_pending: outPending,
          inbound_pending: inPending,
          last_sync_at: lastSync,
        },
      };
    },

    'GET /proxy/config': async () => {
      return {
        body: {
          channel: 'evomap-hub',
          proxy_protocol_version: PROXY_PROTOCOL_VERSION,
          schema_version: SCHEMA_VERSION,
        },
      };
    },

    'GET /proxy/hub-status': async () => {
      if (!getHubMailboxStatus) return { body: { error: 'not_available' } };
      const hubStatus = await getHubMailboxStatus();
      return { body: hubStatus };
    },
  };
}

module.exports = { buildRoutes };
