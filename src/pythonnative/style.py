"""StyleSheet, style resolution, and theming support.

Provides:

- A [`StyleSheet`][pythonnative.StyleSheet] helper for creating and
  composing reusable style dictionaries.
- A [`resolve_style`][pythonnative.style.resolve_style] utility for
  flattening the `style` prop accepted by every component factory.
- A pair of light and dark default themes plus a
  [`ThemeContext`][pythonnative.ThemeContext] for distributing a theme
  dict across a subtree.

Style values are plain Python dicts so they are trivial to compose,
diff, and store. Properties unrecognized by the platform handler are
ignored.

Example:
    ```python
    import pythonnative as pn

    styles = pn.StyleSheet.create(
        title={"font_size": 24, "bold": True, "color": "#333"},
        container={"padding": 16, "spacing": 12},
    )

    pn.Column(
        pn.Text("Hello", style=styles["title"]),
        style=styles["container"],
    )
    ```
"""

from typing import Any, Dict, List, Optional, Union

from .hooks import Context, create_context

_StyleDict = Dict[str, Any]
StyleValue = Union[None, _StyleDict, List[Optional[_StyleDict]]]


def resolve_style(style: StyleValue) -> _StyleDict:
    """Flatten a `style` prop into a single dict.

    Accepts `None`, a single dict, or a list of dicts (later entries
    override earlier ones, mirroring React Native's array-style
    pattern). Used by every built-in element factory in
    `pythonnative.components`.

    Args:
        style: The raw value of the component's `style` argument.

    Returns:
        A flat dict suitable for the native handler. Always a fresh
        dict, never the input.
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
    """Utility for creating, composing, and flattening style dictionaries.

    All methods are stateless and return fresh dicts, so the values can
    be reused safely across components.
    """

    @staticmethod
    def create(**named_styles: _StyleDict) -> Dict[str, _StyleDict]:
        """Create a set of named styles from keyword arguments.

        Args:
            **named_styles: Each keyword argument is a style name
                mapping to a dict of property values.

        Returns:
            A dict mapping each name to a copy of the supplied dict, so
            the caller can mutate the result without affecting the
            originals.

        Example:
            ```python
            from pythonnative import StyleSheet

            styles = StyleSheet.create(
                heading={"font_size": 28, "bold": True},
                body={"font_size": 16},
            )
            ```
        """
        return {name: dict(props) for name, props in named_styles.items()}

    @staticmethod
    def compose(*styles: _StyleDict) -> _StyleDict:
        """Merge multiple style dicts.

        Args:
            *styles: Style dicts to merge. Later dicts override keys
                from earlier ones.

        Returns:
            A new dict containing the merged result. Falsy entries
            (e.g., `None`) are skipped.
        """
        merged: _StyleDict = {}
        for style in styles:
            if style:
                merged.update(style)
        return merged

    @staticmethod
    def flatten(styles: Any) -> _StyleDict:
        """Flatten a style value or list of styles into a single dict.

        Equivalent to
        [`resolve_style`][pythonnative.style.resolve_style] but exposed
        on `StyleSheet` for parity with React Native's API.

        Args:
            styles: A single dict, a list of dicts, or `None`.

        Returns:
            A flat dict combining the inputs.
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
"""Default theme context populated with `DEFAULT_LIGHT_THEME`.

Wrap a subtree in
[`Provider(ThemeContext, my_theme, ...)`][pythonnative.Provider] to
override the theme for that subtree, then read it inside descendants
via [`use_context(ThemeContext)`][pythonnative.use_context].
"""
