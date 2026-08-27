/**
 * FreeAI Dashboard i18n — client-side translation layer.
 * Loads strings from /api/i18n/strings/{locale} and applies them to [data-i18n] elements.
 */
(function () {
  "use strict";
  var locale = (function () {
    var stored = localStorage.getItem("dashboard_locale");
    if (stored) return stored;
    var query = (new URL(document.location.href)).searchParams.get("lang");
    if (query) return query;
    return "en";
  })();

  var strings = {};
  var ready = false;

  function loadStrings(lang) {
    return fetch("/api/i18n/strings/" + lang)
      .then(function (r) { return r.json(); })
      .then(function (data) { strings = data || {}; ready = true; })
      .catch(function () { ready = true; });
  }

  function applyLocale(lang) {
    locale = lang;
    localStorage.setItem("dashboard_locale", lang);
    var isRtl = (lang === "ar");
    document.documentElement.setAttribute("lang", lang);
    document.documentElement.setAttribute("dir", isRtl ? "rtl" : "ltr");
    document.body.classList.toggle("rtl", isRtl);
    document.title = translate("topbar.title");
    applyStrings();
  }

  function translate(key) {
    return strings[key] || key;
  }

  function applyStrings() {
    var els = document.querySelectorAll("[data-i18n]");
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      var key = el.getAttribute("data-i18n");
      var val = strings[key];
      if (val) {
        if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
          el.placeholder = val;
        } else {
          el.textContent = val;
        }
      }
    }
    var placeholders = document.querySelectorAll("[data-i18n-placeholder]");
    for (var j = 0; j < placeholders.length; j++) {
      placeholders[j].placeholder = strings[placeholders[j].getAttribute("data-i18n-placeholder")] || "";
    }
  }

  function setLocale(lang, callback) {
    loadStrings(lang).then(function () {
      applyLocale(lang);
      if (callback) callback();
    });
  }

  function buildSwitcher(container) {
    var sel = document.createElement("select");
    sel.className = "i18n-sel";
    sel.title = "Language";
    var locales = [
      { code: "en", name: "English" },
      { code: "es", name: "Español" },
      { code: "fr", name: "Français" },
      { code: "de", name: "Deutsch" },
      { code: "ja", name: "日本語" },
      { code: "ko", name: "한국어" },
      { code: "zh", name: "中文" },
      { code: "ar", name: "العربية" }
    ];
    for (var i = 0; i < locales.length; i++) {
      var opt = document.createElement("option");
      opt.value = locales[i].code;
      opt.textContent = locales[i].name;
      if (locales[i].code === locale) opt.selected = true;
      sel.appendChild(opt);
    }
    sel.addEventListener("change", function () {
      setLocale(sel.value);
    });
    container.appendChild(sel);
  }

  function init() {
    loadStrings(locale).then(function () {
      applyLocale(locale);
      var switcher = document.querySelector("[data-i18n-switcher]");
      if (switcher) buildSwitcher(switcher);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window._i18n = { translate: translate, setLocale: setLocale, applyLocale: applyLocale };
})();
