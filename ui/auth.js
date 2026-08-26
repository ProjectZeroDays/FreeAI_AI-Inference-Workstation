(function () {
  const KEY = "freeai_auth_token";
  const orig = window.fetch.bind(window);

  window.fetch = function (url, opts = {}) {
    opts.headers = new Headers(opts.headers || {});
    const tok = localStorage.getItem(KEY);
    if (tok && !opts.headers.has("X-Auth-Token")) {
      opts.headers.set("X-Auth-Token", tok);
    }
    return orig(url, opts).then(res => {
      if (res.status === 401) {
        const entered = prompt("Auth token required:");
        if (entered) {
          localStorage.setItem(KEY, entered);
          opts.headers.set("X-Auth-Token", entered);
          return orig(url, opts);
        }
      }
      return res;
    });
  };
})();
