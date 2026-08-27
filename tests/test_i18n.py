"""i18n translation loading, locale detection, RTL, fallback tests."""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

import pytest

from dashboard.i18n import (  # noqa: E402
    t, ngettext, get_supported_locales, is_rtl,
    detect_locale, set_locale_in_session, get_locale_from_session,
    LOCALES_DIR, SUPPORTED, RTL_LOCALES, DEFAULT_LOCALE,
    _load_all, _translations,
)


@pytest.fixture(autouse=True)
def _setup_locales(tmp_path, monkeypatch):
    """Create a temporary locales directory with test translations."""
    locales_dir = tmp_path / "i18n" / "locales"
    locales_dir.mkdir(parents=True)

    # English
    (locales_dir / "en.json").write_text(json.dumps({
        "hello": "Hello",
        "goodbye": "Goodbye",
        "item_count": "{count} items",
        "items_count": "{count} items",
        "welcome": "Welcome",
    }))
    # Spanish
    (locales_dir / "es.json").write_text(json.dumps({
        "hello": "Hola",
        "goodbye": "Adios",
    }))
    # Arabic (RTL)
    (locales_dir / "ar.json").write_text(json.dumps({
        "hello": "مرحبا",
        "goodbye": "مع السلامة",
    }))
    # French
    (locales_dir / "fr.json").write_text(json.dumps({
        "hello": "Bonjour",
    }))

    monkeypatch.setattr("dashboard.i18n.LOCALES_DIR", locales_dir)
    _load_all()
    yield locales_dir


def test_t_returns_translation():
    assert t("hello", "en") == "Hello"
    assert t("hello", "es") == "Hola"
    assert t("hello", "ar") == "مرحبا"


def test_t_fallback_to_english():
    assert t("hello", "de") == "Hello"  # no de translation -> en


def test_t_fallback_to_key_when_missing():
    assert t("nonexistent_key", "en") == "nonexistent_key"


def test_t_invalid_locale_falls_back():
    assert t("hello", "zz") == "Hello"


def test_ngettext_singular():
    result = ngettext("item_count", "items_count", 1, "en")
    assert result == "{count} items"  # ngettext returns the string, no interpolation


def test_ngettext_plural():
    result = ngettext("item_count", "items_count", 5, "en")
    assert result == "{count} items"  # same key for both in this fixture


def test_get_supported_locales():
    locales = get_supported_locales()
    codes = [l["code"] for l in locales]
    assert "en" in codes
    assert "es" in codes
    assert "ar" in codes


def test_is_rtl():
    assert is_rtl("ar") is True
    assert is_rtl("en") is False
    assert is_rtl("es") is False
    assert is_rtl("zh") is False


def test_detect_locale_from_query():
    assert detect_locale(query="es") == "es"
    assert detect_locale(query="ar") == "ar"
    assert detect_locale(query="zz") == DEFAULT_LOCALE  # invalid


def test_detect_locale_from_header():
    assert detect_locale(header="es-ES,en;q=0.9") == "es"
    assert detect_locale(header="fr-FR;quality=0.8") == "fr"
    assert detect_locale(header="en-US,en;q=0.5") == "en"
    assert detect_locale(header="de-DE") == "de"


def test_detect_locale_prefix_match():
    assert detect_locale(header="en-US") == "en"
    assert detect_locale(header="es-MX") == "es"


def test_detect_locale_from_session():
    assert detect_locale(session="fr") == "fr"
    assert detect_locale(session="zz") == DEFAULT_LOCALE


def test_detect_locale_fallback_to_default():
    assert detect_locale() == DEFAULT_LOCALE
    assert detect_locale(header="") == DEFAULT_LOCALE


def test_set_and_get_locale_in_session():
    session = {}
    set_locale_in_session(session, "es")
    assert get_locale_from_session(session) == "es"
    set_locale_in_session(session, "invalid")
    assert get_locale_from_session(session) == "es"  # unchanged


def test_default_locale_is_english():
    assert DEFAULT_LOCALE == "en"


def test_supported_locales_includes_all_expected():
    assert set(SUPPORTED) >= {"en", "es", "fr", "de", "ja", "ko", "zh", "ar"}


def test_translations_loaded_at_startup():
    """Ensure _load_all populates _translations when locales exist."""
    # The fixture patches LOCALES_DIR and calls _load_all,
    # but _load_all rebinds the module-level _translations name.
    # Re-read the current value from the module.
    import dashboard.i18n as _i18n
    _i18n._load_all()
    assert "en" in _i18n._translations
    assert "es" in _i18n._translations
    assert "ar" in _i18n._translations


def test_missing_locale_file_ignored():
    """A malformed JSON file should not crash loading."""
    import dashboard.i18n as _i18n
    locales_dir = _i18n.LOCALES_DIR
    bad_file = locales_dir / "bad.json"
    bad_file.write_text("{invalid json!!!")
    _i18n._load_all()
    # should still have english
    assert "en" in _i18n._translations
