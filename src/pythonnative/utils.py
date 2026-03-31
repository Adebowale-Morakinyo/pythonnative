"""Platform detection and shared helpers.

This module is imported early by most other modules, so it avoids
importing platform-specific packages at module level.
"""

import os
from typing import Any, Optional

# ======================================================================
# Platform detection
# ======================================================================

_is_android: Optional[bool] = None


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


def _ensure_platform_detection() -> None:
    global _is_android
    if _is_android is None:
        _is_android = _detect_android()


def _get_is_android() -> bool:
    _ensure_platform_detection()
    assert _is_android is not None
    return _is_android


IS_ANDROID: bool = _get_is_android()

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
