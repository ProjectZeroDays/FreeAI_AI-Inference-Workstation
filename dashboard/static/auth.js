(function () {
  const ACCESS_KEY = "freeai_access_token";
  const REFRESH_KEY = "freeai_refresh_token";
  const USER_KEY = "freeai_user";
  const orig = window.fetch.bind(window);

  function getToken() { return localStorage.getItem(ACCESS_KEY); }
  function getUser() {
    var raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  }
  function isAuthenticated() { return !!getToken(); }

  // Inject Bearer token on every fetch
  window.fetch = function (url, opts) {
    opts = opts || {};
    opts.headers = new Headers(opts.headers || {});
    var tok = getToken();
    if (tok) {
      opts.headers.set("Authorization", "Bearer " + tok);
    }
    return orig(url, opts).then(function (res) {
      if (res.status === 401) {
        // Try to refresh token
        var refreshTok = localStorage.getItem(REFRESH_KEY);
        if (refreshTok) {
          return fetch("/auth/refresh", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({refresh_token: refreshTok}),
          })
          .then(function (r) { return r.json(); })
          .then(function (data) {
            if (data.access_token) {
              localStorage.setItem(ACCESS_KEY, data.access_token);
              if (data.refresh_token) localStorage.setItem(REFRESH_KEY, data.refresh_token);
              opts.headers.set("Authorization", "Bearer " + data.access_token);
              return orig(url, opts);
            }
            _logoutAndRedirect();
            throw new Error("unauthorized");
          })
          .catch(function () { _logoutAndRedirect(); throw new Error("unauthorized"); });
        }
        _logoutAndRedirect();
        throw new Error("unauthorized");
      }
      return res;
    });
  };

  function _logoutAndRedirect() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    if (window.location.pathname !== "/auth/login") {
      window.location.href = "/auth/login";
    }
  }

  function logout() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.href = "/auth/login";
  }

  // Expose helpers globally
  window.FreeAIAuth = {
    getToken: getToken,
    getUser: getUser,
    isAuthenticated: isAuthenticated,
    logout: logout,
  };
})();

