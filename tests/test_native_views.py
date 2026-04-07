"""Unit tests for the native_views package.

Tests the registry, base handler protocol, and shared utility functions.
Platform-specific handlers (android/ios) are not tested here since they
require their respective runtime environments; they are exercised by
E2E tests on device.
"""

from typing import Any, Dict

import pytest

from pythonnative.native_views import NativeViewRegistry, set_registry
from pythonnative.native_views.base import (
    CONTAINER_KEYS,
    LAYOUT_KEYS,
    ViewHandler,
    is_vertical,
    parse_color_int,
    resolve_padding,
)

# ======================================================================
# parse_color_int
# ======================================================================


def test_parse_color_hex6() -> None:
    result = parse_color_int("#FF0000")
    assert result == parse_color_int("FF0000")
    expected = int("FFFF0000", 16)
    if expected > 0x7FFFFFFF:
        expected -= 0x100000000
    assert result == expected


def test_parse_color_hex8() -> None:
    result = parse_color_int("#80FF0000")
    raw = int("80FF0000", 16)
    expected = raw - 0x100000000  # signed conversion
    assert result == expected


def test_parse_color_int_passthrough() -> None:
    assert parse_color_int(0x00FF00) == 0x00FF00


def test_parse_color_signed_conversion() -> None:
    result = parse_color_int("#FFFFFFFF")
    assert result < 0


def test_parse_color_with_whitespace() -> None:
    assert parse_color_int("  #FF0000  ") == parse_color_int("#FF0000")


# ======================================================================
# resolve_padding
# ======================================================================


def test_resolve_padding_none() -> None:
    assert resolve_padding(None) == (0, 0, 0, 0)


def test_resolve_padding_int() -> None:
    assert resolve_padding(16) == (16, 16, 16, 16)


def test_resolve_padding_float() -> None:
    assert resolve_padding(8.5) == (8, 8, 8, 8)


def test_resolve_padding_dict_horizontal_vertical() -> None:
    result = resolve_padding({"horizontal": 10, "vertical": 20})
    assert result == (10, 20, 10, 20)


def test_resolve_padding_dict_individual() -> None:
    result = resolve_padding({"left": 1, "top": 2, "right": 3, "bottom": 4})
    assert result == (1, 2, 3, 4)


def test_resolve_padding_dict_all() -> None:
    result = resolve_padding({"all": 12})
    assert result == (12, 12, 12, 12)


def test_resolve_padding_unsupported_type() -> None:
    assert resolve_padding("invalid") == (0, 0, 0, 0)


# ======================================================================
# is_vertical
# ======================================================================


def test_is_vertical_column() -> None:
    assert is_vertical("column") is True


def test_is_vertical_column_reverse() -> None:
    assert is_vertical("column_reverse") is True


def test_is_vertical_row() -> None:
    assert is_vertical("row") is False


def test_is_vertical_row_reverse() -> None:
    assert is_vertical("row_reverse") is False


# ======================================================================
# LAYOUT_KEYS / CONTAINER_KEYS
# ======================================================================


def test_layout_keys_contains_expected() -> None:
    expected = {
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
    assert expected == LAYOUT_KEYS


def test_container_keys_contains_expected() -> None:
    expected = {
        "flex_direction",
        "justify_content",
        "align_items",
        "overflow",
        "spacing",
        "padding",
        "background_color",
    }
    assert expected == CONTAINER_KEYS


# ======================================================================
# ViewHandler protocol
# ======================================================================


def test_view_handler_create_raises() -> None:
    handler = ViewHandler()
    with pytest.raises(NotImplementedError):
        handler.create({})


def test_view_handler_update_raises() -> None:
    handler = ViewHandler()
    with pytest.raises(NotImplementedError):
        handler.update(None, {})


def test_view_handler_add_child_noop() -> None:
    handler = ViewHandler()
    handler.add_child(None, None)


def test_view_handler_remove_child_noop() -> None:
    handler = ViewHandler()
    handler.remove_child(None, None)


def test_view_handler_insert_child_delegates() -> None:
    calls: list = []

    class TestHandler(ViewHandler):
        def add_child(self, parent: Any, child: Any) -> None:
            calls.append(("add", parent, child))

    handler = TestHandler()
    handler.insert_child("parent", "child", 0)
    assert calls == [("add", "parent", "child")]


# ======================================================================
# NativeViewRegistry
# ======================================================================


class StubView:
    def __init__(self, type_name: str, props: Dict[str, Any]) -> None:
        self.type_name = type_name
        self.props = dict(props)


class StubHandler(ViewHandler):
    def create(self, props: Dict[str, Any]) -> StubView:
        return StubView("Stub", props)

    def update(self, native_view: Any, changed_props: Dict[str, Any]) -> None:
        native_view.props.update(changed_props)


def test_registry_create_view() -> None:
    reg = NativeViewRegistry()
    reg.register("Text", StubHandler())
    view = reg.create_view("Text", {"text": "hello"})
    assert isinstance(view, StubView)
    assert view.props["text"] == "hello"


def test_registry_unknown_type_raises() -> None:
    reg = NativeViewRegistry()
    with pytest.raises(ValueError, match="Unknown element type"):
        reg.create_view("NonExistent", {})


def test_registry_update_view() -> None:
    reg = NativeViewRegistry()
    reg.register("Text", StubHandler())
    view = reg.create_view("Text", {"text": "old"})
    reg.update_view(view, "Text", {"text": "new"})
    assert view.props["text"] == "new"


def test_registry_update_unknown_type_noop() -> None:
    reg = NativeViewRegistry()
    reg.update_view(StubView("X", {}), "X", {"a": 1})


def test_registry_child_ops_unknown_type_noop() -> None:
    reg = NativeViewRegistry()
    reg.add_child(None, None, "Unknown")
    reg.remove_child(None, None, "Unknown")
    reg.insert_child(None, None, "Unknown", 0)


def test_set_registry_injects() -> None:
    reg = NativeViewRegistry()
    set_registry(reg)
    from pythonnative.native_views import _registry

    assert _registry is reg
    set_registry(None)
