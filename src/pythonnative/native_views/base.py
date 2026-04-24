"""Shared base classes and utilities for native-view handlers.

Provides the [`ViewHandler`][pythonnative.native_views.base.ViewHandler]
protocol implemented by Android and iOS handlers, plus common helpers
for color parsing, padding normalization, and flex-layout constants
shared across platforms.
"""

from typing import Any, Dict, Union


class ViewHandler:
    """Protocol implemented by every native-view handler.

    A `ViewHandler` knows how to create, update, and re-parent native
    views of one element type. The reconciler dispatches through the
    [`NativeViewRegistry`][pythonnative.native_views.NativeViewRegistry];
    handlers never need to know about `Element` or `VNode`.

    Subclasses must override [`create`][pythonnative.native_views.base.ViewHandler.create]
    and [`update`][pythonnative.native_views.base.ViewHandler.update].
    Container handlers override the child-management methods; leaf
    handlers can leave them as no-ops.
    """

    def create(self, props: Dict[str, Any]) -> Any:
        """Create a fresh native view and apply initial props.

        Args:
            props: Initial props dict.

        Returns:
            The platform-native view object.

        Raises:
            NotImplementedError: Subclasses must override.
        """
        raise NotImplementedError

    def update(self, native_view: Any, changed_props: Dict[str, Any]) -> None:
        """Apply only the props that changed since the last render.

        Args:
            native_view: The platform-native view to mutate.
            changed_props: Props whose values changed (a value of
                `None` indicates the prop was removed).

        Raises:
            NotImplementedError: Subclasses must override.
        """
        raise NotImplementedError

    def add_child(self, parent: Any, child: Any) -> None:
        """Append `child` to `parent`. No-op for leaf handlers."""

    def remove_child(self, parent: Any, child: Any) -> None:
        """Remove `child` from `parent`. No-op for leaf handlers."""

    def insert_child(self, parent: Any, child: Any, index: int) -> None:
        """Insert `child` at `index`. Defaults to appending."""
        self.add_child(parent, child)


# ======================================================================
# Color parsing
# ======================================================================


def parse_color_int(color: Union[str, int]) -> int:
    """Parse a color value into a signed 32-bit ARGB int.

    Accepts `"#RRGGBB"`, `"#AARRGGBB"`, or a raw integer. Java APIs
    such as `setBackgroundColor` expect a signed 32-bit int, so values
    with a high alpha byte (e.g., `0xFF......`) must be converted to
    their negative two's-complement equivalent.

    Args:
        color: Hex string (with or without leading `#`) or an int.

    Returns:
        Signed 32-bit ARGB int suitable for Android's color APIs.
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
    """Normalize a padding value to `(left, top, right, bottom)`.

    Accepts:

    - `None`: returns `(0, 0, 0, 0)`.
    - A scalar int/float: same value on all sides.
    - A dict with any of `horizontal`, `vertical`, `left`, `right`,
      `top`, `bottom`, `all` keys.

    Args:
        padding: One of the forms above.

    Returns:
        A 4-tuple of `(left, top, right, bottom)` ints.
    """
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
# Flex layout constants
# ======================================================================

FLEX_DIRECTION_COLUMN = "column"
FLEX_DIRECTION_ROW = "row"
FLEX_DIRECTION_COLUMN_REVERSE = "column_reverse"
FLEX_DIRECTION_ROW_REVERSE = "row_reverse"

JUSTIFY_FLEX_START = "flex_start"
JUSTIFY_CENTER = "center"
JUSTIFY_FLEX_END = "flex_end"
JUSTIFY_SPACE_BETWEEN = "space_between"
JUSTIFY_SPACE_AROUND = "space_around"
JUSTIFY_SPACE_EVENLY = "space_evenly"

ALIGN_STRETCH = "stretch"
ALIGN_FLEX_START = "flex_start"
ALIGN_CENTER = "center"
ALIGN_FLEX_END = "flex_end"

POSITION_RELATIVE = "relative"
POSITION_ABSOLUTE = "absolute"

OVERFLOW_VISIBLE = "visible"
OVERFLOW_HIDDEN = "hidden"
OVERFLOW_SCROLL = "scroll"


def is_vertical(direction: str) -> bool:
    """Return whether `direction` represents a vertical (column) axis."""
    return direction in (FLEX_DIRECTION_COLUMN, FLEX_DIRECTION_COLUMN_REVERSE)


# ======================================================================
# Layout property keys
# ======================================================================

LAYOUT_KEYS = frozenset(
    {
        "width",
        "height",
        "flex",
        "flex_grow",
        "flex_shrink",
        "margin",
        "min_width",
        "max_width",
        "min_height",
        "max_height",
        "align_self",
        "position",
        "top",
        "right",
        "bottom",
        "left",
    }
)

CONTAINER_KEYS = frozenset(
    {
        "flex_direction",
        "justify_content",
        "align_items",
        "overflow",
        "spacing",
        "padding",
        "background_color",
    }
)
