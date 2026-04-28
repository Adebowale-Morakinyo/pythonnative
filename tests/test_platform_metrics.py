"""Tests for the ``pythonnative.platform_metrics`` shared registry.

The page host on each native platform is the only writer; native
view handlers (notably ``TabBarHandler``) are the only readers. The
contract is small but load-bearing, so this suite pins down the
shape, the clamping, and the reset semantics.
"""

import pytest

from pythonnative import platform_metrics
from pythonnative.platform_metrics import (
    SafeAreaInsets,
    get_safe_area_insets,
    reset_safe_area_insets,
    set_safe_area_insets,
)


@pytest.fixture(autouse=True)
def _reset_metrics() -> None:
    """Each test starts with zeroed insets so they are independent."""
    reset_safe_area_insets()


def test_default_insets_are_zero() -> None:
    """Without a page host, handlers see ``(0, 0, 0, 0)``."""
    assert get_safe_area_insets() == SafeAreaInsets(0.0, 0.0, 0.0, 0.0)


def test_set_safe_area_insets_publishes_values() -> None:
    """Values published by the page host are returned verbatim by readers."""
    set_safe_area_insets(top=44.0, left=0.0, bottom=34.0, right=0.0)
    insets = get_safe_area_insets()
    assert insets.top == 44.0
    assert insets.left == 0.0
    assert insets.bottom == 34.0
    assert insets.right == 0.0


def test_set_safe_area_insets_clamps_negative_values() -> None:
    """Negative inputs are coerced to ``0`` to defend handlers from bad native data.

    UIKit and ``WindowInsets`` should never report negative
    insets, but if a defensive ``CGFloat.nan`` slips through or a
    custom shim subtracts past zero, downstream handlers (which
    add the inset to a fixed bar height) would otherwise compute a
    *smaller* tab bar than the spec'd default — masking the bug.
    """
    set_safe_area_insets(top=-1.0, left=-2.0, bottom=-3.0, right=-4.0)
    assert get_safe_area_insets() == SafeAreaInsets(0.0, 0.0, 0.0, 0.0)


def test_set_safe_area_insets_coerces_int_inputs() -> None:
    """Integers are accepted (Android dispatches its dp values as ``int``)."""
    set_safe_area_insets(0, 0, 16, 0)
    assert get_safe_area_insets().bottom == 16.0
    assert isinstance(get_safe_area_insets().bottom, float)


def test_reset_safe_area_insets_restores_zeros() -> None:
    """``reset_safe_area_insets`` returns the registry to its initial state."""
    set_safe_area_insets(10.0, 11.0, 12.0, 13.0)
    reset_safe_area_insets()
    assert get_safe_area_insets() == SafeAreaInsets(0.0, 0.0, 0.0, 0.0)


def test_repeated_set_overwrites_prior_values() -> None:
    """Each ``set_safe_area_insets`` call replaces the published tuple in full."""
    set_safe_area_insets(10.0, 0.0, 0.0, 0.0)
    set_safe_area_insets(0.0, 0.0, 34.0, 0.0)
    assert get_safe_area_insets() == SafeAreaInsets(0.0, 0.0, 34.0, 0.0)


def test_module_state_is_shared_across_imports() -> None:
    """Re-importing the module returns the same singleton state.

    Pin down that handlers reading via ``from .. import
    platform_metrics`` see the same value the page host wrote via
    ``from . import platform_metrics`` — i.e., there is exactly
    one ``_safe_area_insets`` per process.
    """
    set_safe_area_insets(0.0, 0.0, 34.0, 0.0)
    import importlib

    again = importlib.import_module("pythonnative.platform_metrics")
    assert again is platform_metrics
    assert again.get_safe_area_insets().bottom == 34.0


# ======================================================================
# Per-platform tab-bar height contracts
# ======================================================================
#
# These constants and helpers are the single source of truth for both
# native handlers (``ios.TabBarHandler`` and ``android.TabBarHandler``)
# and any future "header / nav-bar wants safe-area" code paths. The
# tests here pin down the visible defaults so a "make it look better"
# refactor cannot silently shrink the bar back to its pre-fix
# squished state.


def test_ios_tab_bar_base_height_matches_uikit_hig() -> None:
    """iOS UITabBar default content height per UIKit HIG is 49 pt."""
    assert platform_metrics.IOS_TAB_BAR_BASE_HEIGHT_PT == 49.0


def test_ios_tab_bar_height_with_no_inset() -> None:
    """Without a published bottom inset, the iOS bar is exactly 49 pt."""
    assert platform_metrics.ios_tab_bar_height() == 49.0


def test_ios_tab_bar_height_includes_bottom_safe_area() -> None:
    """On a device with a 34 pt home-indicator inset, total bar height is 83 pt.

    This matches the iPhone 17 Pro inset measured live in the
    iOS log stream (``insets=(t116.0,l0.0,b34.0,r0.0)``); the bar
    *must* claim that 34 pt or it floats above the home indicator
    with empty space below.

    Android intentionally has no equivalent helper:
    ``BottomNavigationView`` reports a reliable natural height
    once attached, so the Android handler defers to the system.
    Forcing our own height threw off the active-indicator pill
    geometry — see the bug report from screenshot
    ``Screenshot_1777413519`` where the pill partly intersected
    the label.
    """
    set_safe_area_insets(top=0.0, left=0.0, bottom=34.0, right=0.0)
    assert platform_metrics.ios_tab_bar_height() == 83.0


def test_platform_metrics_does_not_export_android_tab_bar_helpers() -> None:
    """Android handler defers to system measure → no helper exists here.

    Pin this so a well-meaning refactor doesn't re-introduce a
    ``android_tab_bar_height_dp`` constant. The previous attempt at
    one shipped two regressions:

    1. ``64 + bottom_inset`` over-counted the gesture indicator and
       made the bar grow on first tab tap.
    2. Even a flat 64 dp threw off the Material 3 active-indicator
       pill, which is positioned against the system's natural
       ``BottomNavigationView`` height (56 dp for label-only,
       80 dp for icon+label).
    """
    assert not hasattr(platform_metrics, "android_tab_bar_height_dp")
    assert not hasattr(platform_metrics, "ANDROID_TAB_BAR_BASE_HEIGHT_DP")
