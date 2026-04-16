"""Platform detection and shared helpers.

This module is imported early by most other modules, so it avoids
importing platform-specific packages at module level.
"""

import os
import sys
from typing import Any, Optional

# ======================================================================
# Platform detection
# ======================================================================

_is_android: Optional[bool] = None
_is_ios: Optional[bool] = None


def _detect_android() -> bool:
    env = os.environ
    if "ANDROID_BOOTLOGO" in env or "ANDROID_ROOT" in env or "ANDROID_DATA" in env or "ANDROID_ARGUMENT" in env:
        return True
    try:
        from java import jclass  # noqa: F401

        return True
    except Exception:
        pass
    return False


def _detect_ios() -> bool:
    """Detect whether we're running inside an iOS app bundle.

    Signals, in priority order:

    - Explicit ``PN_PLATFORM=ios`` env var (set by the iOS template's
      ``ViewController.swift`` before Python starts). This is the
      canonical signal and survives even on hosts where ``sys.platform``
      is generic ``darwin``.
    - ``sys.platform == "ios"`` (CPython 3.13+ native iOS builds).
    - ``/CoreSimulator/Devices/`` in ``$HOME`` (iOS Simulator fallback
      if the template signal is missing for some reason).

    Crucially, having ``rubicon-objc`` importable is *not* enough:
    developers frequently install it on macOS via the ``[ios]`` extra,
    and treating that as iOS would cause subtle side effects
    (e.g. stdout redirection) on desktop machines.
    """
    if os.environ.get("PN_PLATFORM") == "ios":
        return True
    if sys.platform == "ios":
        return True
    home = os.environ.get("HOME", "")
    if "/CoreSimulator/Devices/" in home:
        return True
    return False


def _ensure_platform_detection() -> None:
    global _is_android, _is_ios
    if _is_android is None:
        _is_android = _detect_android()
    if _is_ios is None:
        _is_ios = (not _is_android) and _detect_ios()


def _get_is_android() -> bool:
    _ensure_platform_detection()
    assert _is_android is not None
    return _is_android


def _get_is_ios() -> bool:
    _ensure_platform_detection()
    assert _is_ios is not None
    return _is_ios


IS_ANDROID: bool = _get_is_android()
IS_IOS: bool = _get_is_ios()

# ======================================================================
# Android context management
# ======================================================================

_android_context: Any = None
_android_fragment_container: Any = None


def set_android_context(context: Any) -> None:
    """Record the current Android Activity/Context for view construction."""
    global _android_context
    _android_context = context


def set_android_fragment_container(container_view: Any) -> None:
    """Record the current Fragment root container ViewGroup."""
    global _android_fragment_container
    _android_fragment_container = container_view


def get_android_context() -> Any:
    """Return the current Android Activity/Context."""
    if not IS_ANDROID:
        raise RuntimeError("get_android_context() called on non-Android platform")
    if _android_context is None:
        raise RuntimeError(
            "Android context not set. Ensure Page is initialized from an Activity before constructing views."
        )
    return _android_context


def get_android_fragment_container() -> Any:
    """Return the current Fragment container ViewGroup."""
    if not IS_ANDROID:
        raise RuntimeError("get_android_fragment_container() called on non-Android platform")
    if _android_fragment_container is None:
        raise RuntimeError(
            "Android fragment container not set. Ensure PageFragment has been created before set_root_view."
        )
    return _android_fragment_container
