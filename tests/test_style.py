"""Unit tests for StyleSheet, resolve_style, and theming."""

from pythonnative.style import (
    DEFAULT_DARK_THEME,
    DEFAULT_LIGHT_THEME,
    StyleSheet,
    ThemeContext,
    resolve_style,
)


def test_resolve_style_none() -> None:
    assert resolve_style(None) == {}


def test_resolve_style_dict() -> None:
    result = resolve_style({"font_size": 20, "color": "#000"})
    assert result == {"font_size": 20, "color": "#000"}


def test_resolve_style_list() -> None:
    base = {"font_size": 16, "color": "#000"}
    override = {"color": "#FFF", "bold": True}
    result = resolve_style([base, override])
    assert result == {"font_size": 16, "color": "#FFF", "bold": True}


def test_resolve_style_list_with_none_entries() -> None:
    result = resolve_style([None, {"a": 1}, None, {"b": 2}])
    assert result == {"a": 1, "b": 2}


def test_stylesheet_create() -> None:
    styles = StyleSheet.create(
        heading={"font_size": 28, "bold": True},
        body={"font_size": 16},
    )
    assert "heading" in styles
    assert styles["heading"]["font_size"] == 28
    assert styles["body"]["font_size"] == 16


def test_stylesheet_compose() -> None:
    base = {"font_size": 16, "color": "#000"}
    override = {"color": "#FFF", "bold": True}
    merged = StyleSheet.compose(base, override)
    assert merged["font_size"] == 16
    assert merged["color"] == "#FFF"
    assert merged["bold"] is True


def test_stylesheet_compose_none_safe() -> None:
    result = StyleSheet.compose(None, {"a": 1}, None)
    assert result == {"a": 1}


def test_stylesheet_flatten_dict() -> None:
    result = StyleSheet.flatten({"font_size": 20})
    assert result == {"font_size": 20}


def test_stylesheet_flatten_list() -> None:
    result = StyleSheet.flatten([{"a": 1}, {"b": 2}])
    assert result == {"a": 1, "b": 2}


def test_stylesheet_flatten_none() -> None:
    result = StyleSheet.flatten(None)
    assert result == {}


def test_theme_context_has_default() -> None:
    val = ThemeContext._current()
    assert val is DEFAULT_LIGHT_THEME
    assert "primary_color" in val


def test_light_and_dark_themes_differ() -> None:
    assert DEFAULT_LIGHT_THEME["background_color"] != DEFAULT_DARK_THEME["background_color"]
    assert DEFAULT_LIGHT_THEME["text_color"] != DEFAULT_DARK_THEME["text_color"]
