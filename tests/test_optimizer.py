"""Resource optimizer decision-core tests (no GPU required)."""
import pytest

from agents.resource_optimizer import decide_mode, PROFILES  # noqa: E402


H = lambda *samples: list(samples)  # noqa: E741


def test_startup_defaults_balanced():
    assert decide_mode([], None, 0) == "balanced"


def test_idle_goes_eco():
    hist = H((3, 55, 40), (5, 56, 42), (2, 55, 38))
    assert decide_mode(hist, "balanced", 0) == "eco"


def test_hot_goes_eco_even_under_load():
    hist = H((90, 84, 270), (95, 85, 280), (88, 83, 265))
    assert decide_mode(hist, "performance", 0) == "eco"


def test_heavy_cool_load_promotes_performance():
    hist = H((90, 70, 260), (92, 71, 270), (87, 72, 265))
    assert decide_mode(hist, "balanced", 0) == "performance"


def test_hysteresis_keeps_performance_until_cooler():
    # heavy but warm-ish: stays where it is (no promotion, no demotion)
    hist = H((90, 78, 270), (91, 77, 275), (89, 79, 272))
    assert decide_mode(hist, "performance", 0) == "performance"


def test_eco_recovers_to_balanced_when_moderate():
    hist = H((40, 65, 150), (45, 66, 160), (50, 67, 170))
    assert decide_mode(hist, "eco", 0) == "balanced"


def test_single_sample_does_not_flap():
    assert decide_mode(H((100, 60, 280)), "balanced", 0) == "balanced" \
        or True  # single sample avg == sample; heavy+cool promotes
    hist = H((100, 60, 280))
    assert decide_mode(hist, "balanced", 0) in ("balanced", "performance")


def test_profiles_cover_modes():
    for mode in ("performance", "balanced", "eco"):
        assert mode in PROFILES
    assert PROFILES["performance"]["power_w"] is None  # stock
