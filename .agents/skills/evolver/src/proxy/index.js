'use strict';

const path = require('path');
const os = require('os');
const { MailboxStore } = require('./mailbox/store');
const { ProxyHttpServer } = require('./server/http');
const { buildRoutes } = require('./server/routes');
const { SyncEngine } = require('./sync/engine');
const { LifecycleManager } = require('./lifecycle/manager');
const { TaskMonitor } = require('./task/monitor');
const { SkillUpdater } = require('./extensions/skillUpdater');
const { DmHandler } = require('./extensions/dmHandler');

const DEFAULT_DATA_DIR = path.join(os.homedir(), '.evomap', 'mailbox');

class EvoMapProxy {
  constructor(opts = {}) {
    this.hubUrl = (opts.hubUrl || process.env.A2A_HUB_URL || '').replace(/\/+$/, '');
    this.dataDir = opts.dataDir || opts.dbPath || DEFAULT_DATA_DIR;
    this.port = opts.port;
    this.logger = opts.logger || console;

    this.store = null;
    this.server = null;
    this.sync = null;
    this.lifecycle = null;
    this.taskMonitor = null;
    this.skillUpdater = null;
    this.dmHandler = null;
    this._started = false;
  }

  async start() {
    if (this._started) throw new Error('Proxy already started');

    this.store = new MailboxStore(this.dataDir);

    this.lifecycle = new LifecycleManager({
      hubUrl: this.hubUrl,
      store: this.store,
      logger: this.logger,
      getTaskMeta: () => this.taskMonitor ? this.taskMonitor.getHeartbeatMeta() : {},
    });

    this.taskMonitor = new TaskMonitor({
      store: this.store,
      logger: this.logger,
    });

    this.skillUpdater = new SkillUpdater({
      store: this.store,
      skillPath: opts.skillPath || null,
      logger: this.logger,
    });

    this.dmHandler = new DmHandler({
      store: this.store,
      logger: this.logger,
    });

    const getHeaders = () => this.lifecycle._buildHeaders();
    const taskMonitor = this.taskMonitor;

    this.sync = new SyncEngine({
      store: this.store,
      hubUrl: this.hubUrl,
      getHeaders,
      logger: this.logger,
      onInboundReceived: () => {
        try { this.skillUpdater?.pollAndApply(); } catch {}
      },
    });

    const proxyHandlers = {
      assetFetch: (body) => this._proxyHttp('/a2a/fetch', body),
      assetSearch: (body) => this._proxyHttp('/a2a/assets/search', body),
      assetValidate: (body) => this._proxyHttp('/a2a/validate', body),
    };

    const routes = buildRoutes(this.store, proxyHandlers, this.taskMonitor, {
      dmHandler: this.dmHandler,
      skillUpdater: this.skillUpdater,
      getHubMailboxStatus: () => this._getHubMailboxStatus(),
    });

    const OUTBOUND_ROUTES = [
      'POST /mailbox/send',
      'POST /asset/submit',
      'POST /task/claim',
      'POST /task/complete',
      'POST /task/subscribe',
      'POST /task/unsubscribe',
      'POST /dm/send',
    ];
    for (const key of OUTBOUND_ROUTES) {
      const original = routes[key];
      if (!original) continue;
      routes[key] = async (ctx) => {
        const result = await original(ctx);
        this.sync.notifyNewOutbound();
        return result;
      };
    }

    this.server = new ProxyHttpServer(routes, {
      port: this.port,
      logger: this.logger,
    });

    const serverInfo = await this.server.start();

    if (this.hubUrl) {
      await this.lifecycle.hello();
      this.lifecycle.startHeartbeatLoop();
      this.sync.start();
    } else {
      this.logger.warn('[proxy] No A2A_HUB_URL set, running in offline/local mode');
    }

    this._started = true;

    return {
      url: serverInfo.url,
      port: serverInfo.port,
      nodeId: this.lifecycle.nodeId,
    };
  }

  async stop() {
    if (!this._started) return;
    this.sync?.stop();
    this.lifecycle?.stopHeartbeatLoop();
    await this.server?.stop();
    this.store?.close();
    this._started = false;
    this.logger.log('[proxy] stopped');
  }

  get mailbox() {
    return this.store;
  }

  async _proxyHttp(path, body) {
    if (!this.hubUrl) throw Object.assign(new Error('Hub not configured'), { statusCode: 503 });

    const endpoint = `${this.hubUrl}${path}`;
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: this.lifecycle._buildHeaders(),
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30_000),
    });

    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw Object.assign(new Error(`Hub ${res.status}: ${text}`), { statusCode: res.status });
    }

    return res.json();
  }

  async _getHubMailboxStatus() {
    if (!this.hubUrl) return { error: 'Hub not configured' };
    const endpoint = `${this.hubUrl}/a2a/mailbox/status`;
    try {
      const res = await fetch(endpoint, {
        method: 'GET',
        headers: this.lifecycle._buildHeaders(),
        signal: AbortSignal.timeout(10_000),
      });
      if (!res.ok) return { error: `Hub ${res.status}` };
      return res.json();
    } catch (err) {
      return { error: err.message };
    }
  }
}

async function startProxy(opts = {}) {
  const proxy = new EvoMapProxy(opts);
  const info = await proxy.start();
  return { proxy, ...info };
}

module.exports = { EvoMapProxy, startProxy };
