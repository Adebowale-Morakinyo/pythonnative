"""Platform-level metrics shared between page hosts and view handlers.

The page host (`pythonnative.page`) is the only place that knows
about native window/safe-area state because it is the only piece of
code that holds a reference to the native ``UIViewController``
(iOS) or ``Activity`` (Android). Native view handlers, however, need
that state to size themselves correctly:

- A bottom tab bar must claim both its visible 49 pt / 56 dp content
  height **and** the bottom safe-area inset so its background reaches
  the edge of the screen and the home indicator / gesture bar does
  not draw on top of the labels.
- A future safe-area-aware container can read the same values instead
  of asking each native view for window metrics.

Rather than threading those values through every
[`measure_intrinsic`][pythonnative.native_views.base.ViewHandler.measure_intrinsic]
call signature, the page host writes them here and handlers read
them on demand. Values are in **dp on Android** and **pt on iOS** —
i.e., the same "layout units" the layout engine uses on each
platform, so handlers can add them to other layout-unit values
without further conversion. On iOS the page host consumes the top
safe-area inset by positioning the root view below it, then publishes
``top=0`` here; Android publishes the raw system-bar insets because
the host view normally remains full-screen.

Example:
    >>> from pythonnative.platform_metrics import (
    ...     get_safe_area_insets, set_safe_area_insets,
    ... )
    >>> set_safe_area_insets(top=44.0, left=0.0, bottom=34.0, right=0.0)
    >>> get_safe_area_insets().bottom
    34.0
"""

from __future__ import annotations

from typing import NamedTuple


class SafeAreaInsets(NamedTuple):
    """Safe-area insets in layout units (pt on iOS, dp on Android)."""

    top: float
    left: float
    bottom: float
    right: float


_safe_area_insets: SafeAreaInsets = SafeAreaInsets(0.0, 0.0, 0.0, 0.0)


def set_safe_area_insets(top: float, left: float, bottom: float, right: float) -> None:
    """Publish the current safe-area insets.

    Called by the platform-specific page host whenever it learns a
    new value (e.g., on first layout, on rotation, on multitasking
    split-view changes). Negative inputs are clamped to ``0.0`` so
    handlers don't have to defend against bad data from native
    callers.

    Args:
        top: Distance in layout units from the top of the host
            container to the safe area (status bar / dynamic island /
            navigation bar).
        left: Inset from the left edge.
        bottom: Inset from the bottom edge (home indicator / gesture
            bar).
        right: Inset from the right edge.
    """
    global _safe_area_insets
    _safe_area_insets = SafeAreaInsets(
        max(0.0, float(top)),
        max(0.0, float(left)),
        max(0.0, float(bottom)),
        max(0.0, float(right)),
    )


def get_safe_area_insets() -> SafeAreaInsets:
    """Return the current safe-area insets.

    The default value is ``(0, 0, 0, 0)`` — handlers should still
    function correctly on a desktop / unit-test environment where no
    page host has published insets.
    """
    return _safe_area_insets


def reset_safe_area_insets() -> None:
    """Reset the insets back to ``(0, 0, 0, 0)``.

    Intended for unit tests that need a clean slate between cases.
    Production code should use
    [`set_safe_area_insets`][pythonnative.platform_metrics.set_safe_area_insets]
    instead.
    """
    global _safe_area_insets
    _safe_area_insets = SafeAreaInsets(0.0, 0.0, 0.0, 0.0)


# ======================================================================
# Per-platform tab-bar defaults
# ======================================================================
#
# Only iOS exposes an explicit constant here. The iOS handler can't
# trust ``UITabBar.sizeThatFits_`` (it has historically returned 0 in
# some configurations) and the page host deliberately extends the
# root view past the bottom safe area so the bar reaches the home
# indicator — both pieces conspire to require a single source of
# truth for the height formula.
#
# Android intentionally has no equivalent: ``BottomNavigationView``
# reports a reliable natural height via ``measure(…)`` once attached
# to the window, and the active-indicator pill is positioned against
# that natural height. Forcing our own height threw off the pill
# geometry, so the Android handler defers entirely to the system.

#: UIKit HIG tab-bar content height in points. The total bar reaches
#: ``IOS_TAB_BAR_BASE_HEIGHT_PT + safe_area_insets.bottom`` so the
#: pill background can extend over the home indicator. Apple's HIG
#: places the tab bar flush with the screen edge and lets UIKit
#: render its own internal padding for the home indicator.
IOS_TAB_BAR_BASE_HEIGHT_PT: float = 49.0


def ios_tab_bar_height() -> float:
    """Return the iOS tab-bar intrinsic height in points.

    Equal to ``IOS_TAB_BAR_BASE_HEIGHT_PT + safe_area_insets.bottom``
    so the bar reaches the home indicator. The iOS page host
    deliberately extends the root view past the bottom safe area for
    this very reason — the tab bar absorbs the inset and UIKit
    renders the pill with internal padding for the home indicator.
    Used by ``pythonnative.native_views.ios.TabBarHandler``; exposed
    here so the formula is testable without importing the iOS
    handler module (which requires ``rubicon-objc``).
    """
    return IOS_TAB_BAR_BASE_HEIGHT_PT + get_safe_area_insets().bottom
