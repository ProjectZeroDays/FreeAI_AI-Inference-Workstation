// fingerprint-randomizer: Randomize canvas/WebGL per page to prevent fingerprinting
(function () {
  const _seed = Math.floor(Math.random() * 0xFFFFFFFF) + 1;

  function _hash(str) {
    let h = _seed;
    for (let i = 0; i < str.length; i++) {
      h = ((h << 5) - h) + str.charCodeAt(i);
      h = h & h;
    }
    return Math.abs(h);
  }

  function _noise(val, amount) {
    return val + (Math.sin(_hash(String(val) + _seed)) * amount);
  }

  if (typeof HTMLCanvasElement !== 'undefined') {
    const _origGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (contextType, attrs) {
      const ctx = _origGetContext.call(this, contextType, attrs);
      if (!ctx) return ctx;

      if (contextType === '2d') {
        const _origMeasureText = ctx.measureText;
        ctx.measureText = function (text) {
          const m = _origMeasureText.call(this, text);
          m.width = _noise(m.width, 1.5);
          m.actualBoundingBoxAscent = _noise(m.actualBoundingBoxAscent || 0, 0.5);
          m.actualBoundingBoxDescent = _noise(m.actualBoundingBoxDescent || 0, 0.5);
          return m;
        };
        const _origFillText = ctx.fillText;
        ctx.fillText = function () { return _origFillText.apply(this, arguments); };
      }

      if (contextType.startsWith('webgl')) {
        const _origGetParameter = ctx.getParameter;
        const _vendor = ['Intel Inc.', 'NVIDIA Corporation', 'Apple', 'AMD'][_seed % 4];
        const _renderer = ['ANGLE (Intel, UHD 630)', 'ANGLE (NVIDIA, RTX 3060)', 'ANGLE (Apple, M1 Pro)', 'ANGLE (AMD, RX 6700)'][_seed % 4];
        ctx.getParameter = function (param) {
          if (param === 37445) return _vendor;
          if (param === 37446) return _renderer;
          return _origGetParameter.call(this, param);
        };
        const _origGetShaderPrecisionFormat = ctx.getShaderPrecisionFormat;
        if (_origGetShaderPrecisionFormat) {
          ctx.getShaderPrecisionFormat = function (rt, at) {
            const base = _origGetShaderPrecisionFormat.call(this, rt, at);
            if (!base) return base;
            return {
              ...base,
              rangeMin: Math.max(0, base.rangeMin - 1),
              rangeMax: base.rangeMax + 1,
            };
          };
        }
      }

      return ctx;
    };
  }

  const _origAudioContext = window.AudioContext || window.OfflineAudioContext;
  if (_origAudioContext) {
    const _origStart = _origAudioContext.prototype.start;
    if (_origStart) {
      _origAudioContext.prototype.start = function (when) {
        return _origStart.call(this, when || 0);
      };
    }
  }

  console.log('[fingerprint-randomizer] injected seed=' + _seed);
})();
