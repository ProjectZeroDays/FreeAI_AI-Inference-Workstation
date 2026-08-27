// request-logger: Log all XHR and fetch requests at page level
(function () {
  const log = [];
  const MAX_LOG = 200;

  const _origFetch = window.fetch;
  window.fetch = async function (...args) {
    const url = args[0] instanceof Request ? args[0].url : (args[0] || '');
    const method = args[1]?.method || 'GET';
    const ts = Date.now();
    const entry = { ts, method, url, type: 'fetch' };
    try {
      const resp = await _origFetch.apply(this, args);
      entry.status = resp.status;
      entry.duration = Date.now() - ts;
      log.push(entry);
      if (log.length > MAX_LOG) log.shift();
      return resp;
    } catch (err) {
      entry.error = err.message;
      log.push(entry);
      if (log.length > MAX_LOG) log.shift();
      throw err;
    }
  };

  const origOpen = XMLHttpRequest.prototype.open;
  const origSend = XMLHttpRequest.prototype.send;

  XMLHttpRequest.prototype.open = function (method, url, ...rest) {
    this._ks_method = method;
    this._ks_url = url;
    this._ks_ts = Date.now();
    return origOpen.apply(this, [method, url, ...rest]);
  };

  XMLHttpRequest.prototype.send = function (body) {
    const xhr = this;
    xhr.addEventListener('load', function () {
      const entry = {
        ts: xhr._ks_ts,
        method: xhr._ks_method,
        url: xhr._ks_url,
        status: xhr.status,
        duration: Date.now() - xhr._ks_ts,
        type: 'xhr'
      };
      log.push(entry);
      if (log.length > MAX_LOG) log.shift();
    });
    return origSend.apply(this, arguments);
  };

  window.__ks_request_log = log;
  window.__ks_get_request_log = function () { return log.slice(); };
  window.__ks_clear_request_log = function () { log.length = 0; };

  console.log('[request-logger] injected');
})();
