'use strict';

const { describe, it, before, after, beforeEach } = require('node:test');
const assert = require('node:assert/strict');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { MailboxStore } = require('../src/proxy/mailbox/store');
const { ProxyHttpServer, DEFAULT_PORT } = require('../src/proxy/server/http');
const { buildRoutes } = require('../src/proxy/server/routes');

function tmpDataDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'proxy-test-'));
}

function request(url, method, body) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const payload = body ? JSON.stringify(body) : '';
    const req = http.request({
      hostname: u.hostname,
      port: u.port,
      path: u.pathname + u.search,
      method,
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
      },
    }, (res) => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        const raw = Buffer.concat(chunks).toString();
        try { resolve({ status: res.statusCode, body: JSON.parse(raw) }); }
        catch { resolve({ status: res.statusCode, body: raw }); }
      });
    });
    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

describe('ProxyHttpServer', () => {
  let store, server, baseUrl, dataDir;

  before(async () => {
    dataDir = tmpDataDir();
    store = new MailboxStore(dataDir);

    const mockProxyHandlers = {
      assetFetch: async (body) => ({ assets: [], query: body }),
      assetSearch: async (body) => ({ results: [], query: body }),
      assetValidate: async (body) => ({ valid: true, asset_id: body.asset_id || 'test' }),
    };

    const routes = buildRoutes(store, mockProxyHandlers, null, {});

    server = new ProxyHttpServer(routes, { port: 39820, logger: { log: () => {}, error: () => {}, warn: () => {} } });
    const info = await server.start();
    baseUrl = info.url;
  });

  after(async () => {
    await server.stop();
    store.close();
    try { fs.rmSync(dataDir, { recursive: true }); } catch {}
  });

  describe('POST /mailbox/send', () => {
    it('sends a message and returns message_id', async () => {
      const res = await request(`${baseUrl}/mailbox/send`, 'POST', {
        type: 'asset_submit',
        payload: { data: 'test' },
      });
      assert.equal(res.status, 200);
      assert.ok(res.body.message_id);
      assert.equal(res.body.status, 'pending');
    });

    it('rejects missing type', async () => {
      const res = await request(`${baseUrl}/mailbox/send`, 'POST', {
        payload: { data: 'test' },
      });
      assert.equal(res.status, 400);
    });

    it('rejects missing payload', async () => {
      const res = await request(`${baseUrl}/mailbox/send`, 'POST', {
        type: 'test',
      });
      assert.equal(res.status, 400);
    });
  });

  describe('POST /mailbox/poll', () => {
    it('returns inbound messages', async () => {
      store.writeInbound({ type: 'poll_test', payload: { x: 1 } });
      const res = await request(`${baseUrl}/mailbox/poll`, 'POST', {
        type: 'poll_test',
      });
      assert.equal(res.status, 200);
      assert.ok(res.body.messages.length >= 1);
    });
  });

  describe('POST /mailbox/ack', () => {
    it('acknowledges messages', async () => {
      const id = store.writeInbound({ type: 'ack_test', payload: {} });
      const res = await request(`${baseUrl}/mailbox/ack`, 'POST', {
        message_ids: [id],
      });
      assert.equal(res.status, 200);
      assert.equal(res.body.acknowledged, 1);
    });

    it('rejects missing message_ids', async () => {
      const res = await request(`${baseUrl}/mailbox/ack`, 'POST', {});
      assert.equal(res.status, 400);
    });
  });

  describe('GET /mailbox/status/:id', () => {
    it('returns message details', async () => {
      const { message_id } = store.send({ type: 'status_test', payload: { test: true } });
      const res = await request(`${baseUrl}/mailbox/status/${message_id}`, 'GET');
      assert.equal(res.status, 200);
      assert.equal(res.body.id, message_id);
      assert.equal(res.body.type, 'status_test');
    });

    it('returns 404 for unknown id', async () => {
      const res = await request(`${baseUrl}/mailbox/status/nonexistent`, 'GET');
      assert.equal(res.status, 404);
    });
  });

  describe('GET /mailbox/list', () => {
    it('lists messages by type', async () => {
      store.send({ type: 'list_http_test', payload: {} });
      const res = await request(`${baseUrl}/mailbox/list?type=list_http_test`, 'GET');
      assert.equal(res.status, 200);
      assert.ok(res.body.messages.length >= 1);
    });

    it('requires type query param', async () => {
      const res = await request(`${baseUrl}/mailbox/list`, 'GET');
      assert.equal(res.status, 400);
    });
  });

  describe('POST /asset/submit', () => {
    it('queues asset submission via mailbox', async () => {
      const res = await request(`${baseUrl}/asset/submit`, 'POST', {
        assets: [{ type: 'Gene', content: 'test' }],
      });
      assert.equal(res.status, 200);
      assert.ok(res.body.message_id);
    });

    it('rejects missing assets and asset_id', async () => {
      const res = await request(`${baseUrl}/asset/submit`, 'POST', {
        priority: 'high',
      });
      assert.equal(res.status, 400);
    });
  });

  describe('POST /asset/validate', () => {
    it('validates asset via proxy', async () => {
      const res = await request(`${baseUrl}/asset/validate`, 'POST', {
        asset_id: 'sha256:abc',
      });
      assert.equal(res.status, 200);
      assert.equal(res.body.valid, true);
    });

    it('rejects missing asset_id and assets', async () => {
      const res = await request(`${baseUrl}/asset/validate`, 'POST', {});
      assert.equal(res.status, 400);
    });
  });

  describe('GET /asset/submissions', () => {
    it('lists asset submissions with results', async () => {
      store.send({ type: 'asset_submit', payload: { assets: [{ type: 'Gene' }] } });
      const res = await request(`${baseUrl}/asset/submissions`, 'GET');
      assert.equal(res.status, 200);
      assert.ok(Array.isArray(res.body.submissions));
      assert.ok(res.body.count >= 1);
    });
  });

  describe('POST /asset/fetch', () => {
    it('proxies fetch request (mock)', async () => {
      const res = await request(`${baseUrl}/asset/fetch`, 'POST', {
        asset_ids: ['sha256:abc'],
      });
      assert.equal(res.status, 200);
      assert.ok(res.body.assets);
    });
  });

  describe('POST /asset/search', () => {
    it('proxies search request (mock)', async () => {
      const res = await request(`${baseUrl}/asset/search`, 'POST', {
        signals: ['log_error'],
        mode: 'semantic',
      });
      assert.equal(res.status, 200);
      assert.ok(res.body.results);
    });
  });

  describe('Task routes', () => {
    it('POST /task/subscribe returns message_id', async () => {
      const res = await request(`${baseUrl}/task/subscribe`, 'POST', {});
      assert.equal(res.status, 200);
      assert.ok(res.body.message_id);
    });

    it('POST /task/claim requires task_id', async () => {
      const res = await request(`${baseUrl}/task/claim`, 'POST', {});
      assert.equal(res.status, 400);
    });

    it('POST /task/claim accepts valid task_id', async () => {
      const res = await request(`${baseUrl}/task/claim`, 'POST', { task_id: 'task_123' });
      assert.equal(res.status, 200);
      assert.ok(res.body.message_id);
    });

    it('POST /task/complete requires task_id', async () => {
      const res = await request(`${baseUrl}/task/complete`, 'POST', {});
      assert.equal(res.status, 400);
    });

    it('POST /task/complete accepts valid data', async () => {
      const res = await request(`${baseUrl}/task/complete`, 'POST', {
        task_id: 'task_123',
        asset_id: 'sha256:abc',
      });
      assert.equal(res.status, 200);
      assert.ok(res.body.message_id);
    });
  });

  describe('GET /task/metrics', () => {
    it('returns task metrics (null monitor)', async () => {
      const res = await request(`${baseUrl}/task/metrics`, 'GET');
      assert.equal(res.status, 200);
      assert.equal(res.body.subscribed, false);
    });
  });

  describe('DM routes', () => {
    it('POST /dm/send sends a direct message', async () => {
      const res = await request(`${baseUrl}/dm/send`, 'POST', {
        recipient_node_id: 'node_xyz',
        content: 'Hello from test',
      });
      assert.equal(res.status, 200);
      assert.ok(res.body.message_id);
    });

    it('POST /dm/send rejects missing recipient', async () => {
      const res = await request(`${baseUrl}/dm/send`, 'POST', {
        content: 'Hello',
      });
      assert.equal(res.status, 400);
    });

    it('POST /dm/send rejects missing content', async () => {
      const res = await request(`${baseUrl}/dm/send`, 'POST', {
        recipient_node_id: 'node_xyz',
      });
      assert.equal(res.status, 400);
    });

    it('POST /dm/poll returns DM messages', async () => {
      store.writeInbound({ type: 'dm', payload: { content: 'test dm' } });
      const res = await request(`${baseUrl}/dm/poll`, 'POST', {});
      assert.equal(res.status, 200);
      assert.ok(Array.isArray(res.body.messages));
    });

    it('GET /dm/list lists DM history', async () => {
      const res = await request(`${baseUrl}/dm/list`, 'GET');
      assert.equal(res.status, 200);
      assert.ok(Array.isArray(res.body.messages));
    });
  });

  describe('GET /proxy/status', () => {
    it('returns proxy status with version info', async () => {
      const res = await request(`${baseUrl}/proxy/status`, 'GET');
      assert.equal(res.status, 200);
      assert.equal(res.body.status, 'running');
      assert.ok('outbound_pending' in res.body);
      assert.ok('inbound_pending' in res.body);
      assert.ok(res.body.proxy_protocol_version, 'should include proxy_protocol_version');
      assert.ok(res.body.schema_version, 'should include schema_version');
      assert.match(res.body.proxy_protocol_version, /^\d+\.\d+\.\d+$/);
    });
  });

  describe('404 handling', () => {
    it('returns 404 for unknown routes', async () => {
      const res = await request(`${baseUrl}/nonexistent`, 'GET');
      assert.equal(res.status, 404);
    });
  });
});
