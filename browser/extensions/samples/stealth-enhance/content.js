// stealth-enhance: Additional navigator/runtime overrides
(function () {
  const _t = Date.now();
  const _seed = Math.floor(Math.random() * 0xFFFFFFFF);

  Object.defineProperty(navigator, 'userAgentData', {
    get: function () {
      return {
        brands: [{ brand: 'Chromium', version: '120' }, { brand: 'Not.A-Brand', version: '24' }],
        mobile: false,
        platform: 'Windows',
        getHighEntropyValues: async function (hints) { return { platform: 'Windows' }; }
      };
    }
  });

  Object.defineProperty(navigator, 'webkitPersistentStorage', { get: () => 0 });
  Object.defineProperty(navigator, 'webkitTemporaryStorage', { get: () => 0 });
  Object.defineProperty(navigator, 'registerProtocolHandler', { value: function () { return false; } });
  Object.defineProperty(navigator, 'unregisterProtocolHandler', { value: function () { return false; } });

  if (!window.chrome || !window.chrome.runtime) {
    window.chrome = window.chrome || {};
    window.chrome.runtime = {
      id: undefined,
      onMessage: { addListener: function () {} },
      sendMessage: function () {}
    };
  }

  const _origQuery = window.matchMedia;
  window.matchMedia = function (query) {
    if (query === '(prefers-color-scheme: dark)') {
      return { matches: false, media: query, onchange: null, addListener: function () {}, removeListener: function () {} };
    }
    if (query === '(forced-colors: active)') {
      return { matches: false, media: query, onchange: null, addListener: function () {}, removeListener: function () {} };
    }
    return _origQuery.call(window, query);
  };
  window.matchMedia.toString = function () { return 'function matchMedia() { [native code] }'; };

  const _origGetGamepads = navigator.getGamepads;
  if (_origGetGamepads) {
    navigator.getGamepads = function () { return []; };
  }

  delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
  delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
  delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
  delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
  delete window.cdc_adoQpoasnfa76pfcZLmcfl_Serializer;

  if (typeof HTMLCanvasElement !== 'undefined') {
    const _origToBlob = HTMLCanvasElement.prototype.toBlob;
    if (_origToBlob) {
      HTMLCanvasElement.prototype.toBlob = function (cb) {
        const args = Array.prototype.slice.call(arguments);
        const origCb = args[0];
        args[0] = function (blob) {
          if (blob) { blob.lastTouch = Date.now(); }
          origCb(blob);
        };
        return _origToBlob.apply(this, args);
      };
    }
  }

  const _origQuerySelectorAll = Document.prototype.querySelectorAll;
  Document.prototype.querySelectorAll = function (selector) {
    if (selector === '.cdc_adoQpoasnfa76pfcZLmcfl') return _origQuerySelectorAll.apply(this, []);
    return _origQuerySelectorAll.apply(this, arguments);
  };

  console.log('[stealth-enhance] injected');
})();
