"""Shared base classes and utilities for native view handlers.

Provides the :class:`ViewHandler` abstract base class and common helper
functions used by both Android and iOS platform implementations.
"""

from typing import Any, Dict, Union


class ViewHandler:
    """Protocol for creating, updating, and managing children of a native view type."""

    def create(self, props: Dict[str, Any]) -> Any:
        raise NotImplementedError

    def update(self, native_view: Any, changed_props: Dict[str, Any]) -> None:
        raise NotImplementedError

    def add_child(self, parent: Any, child: Any) -> None:
        pass

    def remove_child(self, parent: Any, child: Any) -> None:
        pass

    def insert_child(self, parent: Any, child: Any, index: int) -> None:
        self.add_child(parent, child)


# ======================================================================
# Color parsing
# ======================================================================


def parse_color_int(color: Union[str, int]) -> int:
    """Parse ``#RRGGBB`` / ``#AARRGGBB`` hex string or raw int to a *signed* ARGB int.

    Java's ``setBackgroundColor`` et al. expect a signed 32-bit int, so values
    with a high alpha byte (e.g. 0xFF…) must be converted to negative ints.
    """
    if isinstance(color, int):
        val = color
    else:
        c = color.strip().lstrip("#")
        if len(c) == 6:
            c = "FF" + c
        val = int(c, 16)
    if val > 0x7FFFFFFF:
        val -= 0x100000000
    return val


# ======================================================================
# Padding / margin helpers
# ======================================================================


def resolve_padding(padding: Any) -> tuple:
    """Normalise various padding representations to ``(left, top, right, bottom)``."""
    if padding is None:
        return (0, 0, 0, 0)
    if isinstance(padding, (int, float)):
        v = int(padding)
        return (v, v, v, v)
    if isinstance(padding, dict):
        h = int(padding.get("horizontal", 0))
        v = int(padding.get("vertical", 0))
        left = int(padding.get("left", h))
        right = int(padding.get("right", h))
        top = int(padding.get("top", v))
        bottom = int(padding.get("bottom", v))
        a = int(padding.get("all", 0))
        if a:
            left = left or a
            right = right or a
            top = top or a
            bottom = bottom or a
        return (left, top, right, bottom)
    return (0, 0, 0, 0)


# ======================================================================
# Layout property keys
# ======================================================================

LAYOUT_KEYS = frozenset(
    {
        "width",
        "height",
        "flex",
        "margin",
        "min_width",
        "max_width",
        "min_height",
        "max_height",
        "align_self",
    }
)
