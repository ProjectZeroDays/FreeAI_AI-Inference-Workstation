"""FreeAI Dashboard i18n — lightweight JSON-backed translation system."""
import json
import threading
from pathlib import Path

LOCALES_DIR = Path(__file__).parent / "i18n" / "locales"
SUPPORTED = ["en", "es", "fr", "de", "ja", "ko", "zh", "ar"]
RTL_LOCALES = {"ar"}
DEFAULT_LOCALE = "en"

_lock = threading.Lock()
_translations: dict[str, dict[str, str]] = {}
_locale_map: dict[str, str] = {"en": "English", "es": "Español", "fr": "Français",
                                "de": "Deutsch", "ja": "日本語", "ko": "한국어",
                                "zh": "中文", "ar": "العربية"}


def _load_all():
    global _translations
    with _lock:
        _translations = {}
        if not LOCALES_DIR.exists():
            return
        for f in sorted(LOCALES_DIR.glob("*.json")):
            code = f.stem.lower()
            if code in SUPPORTED:
                try:
                    _translations[code] = json.loads(f.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    pass
        # ensure en always loaded
        if "en" not in _translations:
            _translations["en"] = {}


def _get(key: str, locale: str) -> str:
    with _lock:
        data = _translations.get(locale) or _translations.get(DEFAULT_LOCALE) or {}
    return data.get(key, key)


def t(key: str, locale: str = DEFAULT_LOCALE) -> str:
    if locale not in SUPPORTED:
        locale = DEFAULT_LOCALE
    return _get(key, locale)


def ngettext(key_singular: str, key_plural: str, count: int,
             locale: str = DEFAULT_LOCALE) -> str:
    if count == 1:
        return t(key_singular, locale)
    return t(key_plural, locale)


def get_supported_locales() -> list[dict]:
    return [{"code": c, "name": _locale_map.get(c, c)} for c in SUPPORTED]


def is_rtl(locale: str) -> bool:
    return locale in RTL_LOCALES


def detect_locale(header: str = "", query: str = "", session: str = "") -> str:
    """Return best-guess locale from Accept-Language header, query param, or session."""
    if query and query in SUPPORTED:
        return query
    if header:
        for part in header.replace(";", ",").split(","):
            part = part.strip()
            code = part.split(";")[0].strip().lower()
            if code in SUPPORTED:
                return code
            # try prefix match e.g. "en-us" -> "en"
            prefix = code.split("-")[0]
            if prefix in SUPPORTED:
                return prefix
    if session in SUPPORTED:
        return session
    return DEFAULT_LOCALE


def set_locale_in_session(session: dict, locale: str) -> None:
    if locale in SUPPORTED:
        session["dashboard_locale"] = locale


def get_locale_from_session(session: dict) -> str:
    return session.get("dashboard_locale", DEFAULT_LOCALE)


# ── Jinja2 extensions (loaded by backend.py) ─────────────────────

def _jinja_t(key: str, locale: str = DEFAULT_LOCALE) -> str:
    return t(key, locale)


def add_jinja_extensions(app):
    """Attach t() and i18n helpers to Jinja2 environment."""
    app.jinja_env.globals["t"] = _jinja_t
    app.jinja_env.globals["IS_RTL"] = is_rtl
    app.jinja_env.globals["get_supported_locales"] = get_supported_locales
    app.jinja_env.globals["DEFAULT_LOCALE"] = DEFAULT_LOCALE
    app.jinja_env.globals["SUPPORTED_LOCALES"] = SUPPORTED

    @app.context_processor
    def _i18n_ctx():
        # Use session locale if available, else default
        from flask import session
        locale = get_locale_from_session(session)
        return {
            "i18n_locale": locale,
            "i18n_is_rtl": is_rtl(locale),
            "i18n_supported_locales": get_supported_locales(),
        }
