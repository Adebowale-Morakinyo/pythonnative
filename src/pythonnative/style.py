"""StyleSheet, style resolution, and theming support.

Provides a :class:`StyleSheet` helper for creating and composing
reusable style dictionaries, a :func:`resolve_style` utility for
flattening the ``style`` prop, and built-in theme contexts.

Usage::

    import pythonnative as pn

    styles = pn.StyleSheet.create(
        title={"font_size": 24, "bold": True, "color": "#333"},
        container={"padding": 16, "spacing": 12},
    )

    pn.Text("Hello", style=styles["title"])
    pn.Column(..., style=styles["container"])
"""

from typing import Any, Dict, List, Optional, Union

from .hooks import Context, create_context

_StyleDict = Dict[str, Any]
StyleValue = Union[None, _StyleDict, List[Optional[_StyleDict]]]


def resolve_style(style: StyleValue) -> _StyleDict:
    """Flatten a ``style`` prop into a single dict.

    Accepts ``None``, a single dict, or a list of dicts (later entries
    override earlier ones, mirroring React Native's array style pattern).
    """
    if style is None:
        return {}
    if isinstance(style, dict):
        return dict(style)
    result: _StyleDict = {}
    for entry in style:
        if entry:
            result.update(entry)
    return result


# ======================================================================
# StyleSheet
# ======================================================================


class StyleSheet:
    """Utility for creating and composing style dictionaries."""

    @staticmethod
    def create(**named_styles: _StyleDict) -> Dict[str, _StyleDict]:
        """Create a set of named styles.

        Each keyword argument is a style name mapping to a dict of
        property values::

            styles = StyleSheet.create(
                heading={"font_size": 28, "bold": True},
                body={"font_size": 16},
            )
        """
        return {name: dict(props) for name, props in named_styles.items()}

    @staticmethod
    def compose(*styles: _StyleDict) -> _StyleDict:
        """Merge multiple style dicts, later values overriding earlier ones."""
        merged: _StyleDict = {}
        for style in styles:
            if style:
                merged.update(style)
        return merged

    @staticmethod
    def flatten(styles: Any) -> _StyleDict:
        """Flatten a style or list of styles into a single dict.

        Accepts a single dict, a list of dicts, or ``None``.
        """
        if styles is None:
            return {}
        if isinstance(styles, dict):
            return dict(styles)
        result: _StyleDict = {}
        for s in styles:
            if s:
                result.update(s)
        return result


# ======================================================================
# Theming
# ======================================================================

DEFAULT_LIGHT_THEME: _StyleDict = {
    "primary_color": "#007AFF",
    "secondary_color": "#5856D6",
    "background_color": "#FFFFFF",
    "surface_color": "#F2F2F7",
    "text_color": "#000000",
    "text_secondary_color": "#8E8E93",
    "error_color": "#FF3B30",
    "success_color": "#34C759",
    "warning_color": "#FF9500",
    "font_size": 16,
    "font_size_small": 13,
    "font_size_large": 20,
    "font_size_title": 28,
    "spacing": 8,
    "spacing_large": 16,
    "border_radius": 8,
}

DEFAULT_DARK_THEME: _StyleDict = {
    "primary_color": "#0A84FF",
    "secondary_color": "#5E5CE6",
    "background_color": "#000000",
    "surface_color": "#1C1C1E",
    "text_color": "#FFFFFF",
    "text_secondary_color": "#8E8E93",
    "error_color": "#FF453A",
    "success_color": "#30D158",
    "warning_color": "#FF9F0A",
    "font_size": 16,
    "font_size_small": 13,
    "font_size_large": 20,
    "font_size_title": 28,
    "spacing": 8,
    "spacing_large": 16,
    "border_radius": 8,
}

ThemeContext: Context = create_context(DEFAULT_LIGHT_THEME)
