'use strict';

const http = require('http');
const { writeSettings, readSettings, clearSettings, clearIfStale } = require('./settings');

const MAX_PORT_ATTEMPTS = 100;
const DEFAULT_PORT = 19820;

function parseBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', c => chunks.push(c));
    req.on('end', () => {
      const raw = Buffer.concat(chunks).toString();
      if (!raw) return resolve({});
      try { resolve(JSON.parse(raw)); }
      catch (e) { reject(new Error('Invalid JSON body')); }
    });
    req.on('error', reject);
  });
}

function sendJson(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(payload),
  });
  res.end(payload);
}

function tryListen(server, port) {
  return new Promise((resolve, reject) => {
    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE') return resolve(false);
      reject(err);
    });
    server.listen(port, '127.0.0.1', () => resolve(true));
  });
}

class ProxyHttpServer {
  constructor(routes, { port, logger } = {}) {
    this.routes = routes;
    this.basePort = port || Number(process.env.EVOMAP_PROXY_PORT) || DEFAULT_PORT;
    this.actualPort = null;
    this.logger = logger || console;
    this.server = null;
  }

  async start() {
    clearIfStale();
    this.server = http.createServer((req, res) => this._handleRequest(req, res));

    let port = this.basePort;
    for (let i = 0; i < MAX_PORT_ATTEMPTS; i++) {
      const ok = await tryListen(this.server, port);
      if (ok) {
        this.actualPort = port;
        const url = `http://127.0.0.1:${port}`;
        writeSettings({
          proxy: {
            url,
            pid: process.pid,
            started_at: new Date().toISOString(),
          },
        });
        this.logger.log(`[proxy] HTTP server listening on ${url}`);
        return { port, url };
      }
      port++;
    }
    throw new Error(`Could not find free port after ${MAX_PORT_ATTEMPTS} attempts starting from ${this.basePort}`);
  }

  async stop() {
    if (this.server) {
      await new Promise((resolve) => this.server.close(resolve));
      this.server = null;
    }
    clearSettings();
  }

  async _handleRequest(req, res) {
    const url = new URL(req.url, `http://127.0.0.1:${this.actualPort}`);
    const routeKey = `${req.method} ${url.pathname}`;

    const paramMatch = this._matchRoute(req.method, url.pathname);

    if (!paramMatch) {
      return sendJson(res, 404, { error: 'Not found', path: url.pathname });
    }

    const { handler, params } = paramMatch;

    try {
      const body = (req.method === 'POST' || req.method === 'PUT') ? await parseBody(req) : {};
      const query = Object.fromEntries(url.searchParams);
      const result = await handler({ body, query, params });
      sendJson(res, result.status || 200, result.body || result);
    } catch (err) {
      this.logger.error(`[proxy] ${routeKey} error:`, err.message);
      sendJson(res, err.statusCode || 500, {
        error: err.message || 'Internal error',
      });
    }
  }

  _matchRoute(method, pathname) {
    for (const [pattern, handler] of Object.entries(this.routes)) {
      const [routeMethod, routePath] = pattern.split(' ');
      if (routeMethod !== method) continue;

      const params = matchPath(routePath, pathname);
      if (params !== null) return { handler, params };
    }
    return null;
  }
}

function matchPath(pattern, pathname) {
  const patternParts = pattern.split('/');
  const pathParts = pathname.split('/');

  if (patternParts.length !== pathParts.length) return null;

  const params = {};
  for (let i = 0; i < patternParts.length; i++) {
    if (patternParts[i].startsWith(':')) {
      params[patternParts[i].slice(1)] = pathParts[i];
    } else if (patternParts[i] !== pathParts[i]) {
      return null;
    }
  }
  return params;
}

module.exports = { ProxyHttpServer, parseBody, sendJson, DEFAULT_PORT };
