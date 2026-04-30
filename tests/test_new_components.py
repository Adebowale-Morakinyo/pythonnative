"""Unit tests for the new components: StatusBar, KeyboardAvoidingView, Picker, Sectionlist, etc."""

from __future__ import annotations

from pythonnative.components import (
    FlatList,
    KeyboardAvoidingView,
    Picker,
    RefreshControl,
    SectionList,
    StatusBar,
    Text,
)

# ======================================================================
# StatusBar
# ======================================================================


def test_status_bar_default() -> None:
    el = StatusBar()
    assert el.type == "StatusBar"
    assert el.children == []
    assert el.props == {}


def test_status_bar_style_and_hidden() -> None:
    el = StatusBar(style="dark", background_color="#FFFFFF", hidden=False)
    assert el.props["style"] == "dark"
    assert el.props["background_color"] == "#FFFFFF"
    assert el.props["hidden"] is False


# ======================================================================
# KeyboardAvoidingView
# ======================================================================


def test_keyboard_avoiding_default_behavior() -> None:
    el = KeyboardAvoidingView(Text("hi"))
    assert el.type == "KeyboardAvoidingView"
    assert el.props["behavior"] == "padding"
    assert len(el.children) == 1


def test_keyboard_avoiding_custom_behavior() -> None:
    el = KeyboardAvoidingView(Text("hi"), behavior="position")
    assert el.props["behavior"] == "position"


# ======================================================================
# RefreshControl
# ======================================================================


def test_refresh_control_dict_shape() -> None:
    cb = lambda: None  # noqa: E731
    spec = RefreshControl(refreshing=True, on_refresh=cb, tint_color="#FF0000")
    assert isinstance(spec, dict)
    assert spec["refreshing"] is True
    assert spec["on_refresh"] is cb
    assert spec["tint_color"] == "#FF0000"


def test_refresh_control_minimal() -> None:
    spec = RefreshControl()
    assert spec == {"refreshing": False}


# ======================================================================
# Picker
# ======================================================================


def test_picker_renders_pressable_with_label() -> None:
    el = Picker(
        value="b",
        items=[
            {"value": "a", "label": "Apple"},
            {"value": "b", "label": "Banana"},
        ],
        on_change=lambda _: None,
    )
    assert el.type == "Pressable"
    assert el.props.get("on_press") is not None
    # The child should be a Text with the selected label.
    assert el.children[0].type == "Text"
    assert el.children[0].props["text"] == "Banana"


def test_picker_placeholder_when_no_match() -> None:
    el = Picker(
        value="zzz",
        items=[{"value": "a", "label": "Apple"}],
        placeholder="Pick one",
    )
    assert el.children[0].props["text"] == "Pick one"


# ======================================================================
# Virtualized FlatList
# ======================================================================


def test_flatlist_eager_when_no_item_height() -> None:
    items = [{"id": i, "name": f"Item {i}"} for i in range(3)]
    el = FlatList(
        data=items,
        render_item=lambda item, _i: Text(item["name"]),
        key_extractor=lambda item, _i: str(item["id"]),
    )
    assert el.type == "ScrollView"
    inner = el.children[0]
    assert inner.type == "Column"
    assert len(inner.children) == 3
    assert inner.children[0].key == "0"


def test_flatlist_virtualized_when_item_height_set() -> None:
    items = list(range(100))
    el = FlatList(
        data=items,
        item_height=44,
        render_item=lambda item, _i: Text(str(item)),
    )
    assert el.type == "VirtualList"
    assert el.props["count"] == 100
    assert el.props["row_height"] == 44.0
    assert callable(el.props["mount_row"])


def test_flatlist_virtualized_with_separator() -> None:
    el = FlatList(
        data=[1, 2, 3],
        item_height=20,
        separator_height=4,
    )
    assert el.props["row_height"] == 24.0


def test_flatlist_with_refresh_control() -> None:
    el = FlatList(
        data=[1, 2],
        item_height=20,
        refresh_control={"refreshing": True, "on_refresh": lambda: None},
    )
    assert el.props["refresh_control"]["refreshing"] is True


def test_flatlist_on_item_press_propagated() -> None:
    cb = lambda i: None  # noqa: E731
    el = FlatList(data=[1, 2], item_height=20, on_item_press=cb)
    assert el.props["on_row_press"] is cb


# ======================================================================
# SectionList
# ======================================================================


def test_section_list_eager_default() -> None:
    sections = [
        {"title": "A", "data": ["a1", "a2"]},
        {"title": "B", "data": ["b1"]},
    ]
    el = SectionList(sections=sections)
    assert el.type == "ScrollView"
    inner = el.children[0]
    # 2 headers + 3 items = 5 rows.
    assert len(inner.children) == 5
    assert inner.children[0].props["text"] == "A"
    assert inner.children[1].props["text"] == "a1"


def test_section_list_virtualized() -> None:
    sections = [
        {"title": "X", "data": list(range(50))},
        {"title": "Y", "data": list(range(50))},
    ]
    el = SectionList(sections=sections, item_height=30, section_header_height=40)
    assert el.type == "VirtualList"
    # 2 headers + 100 items.
    assert el.props["count"] == 102
    assert el.props["row_height"] == 40.0  # max of 40 and 30+0
    assert callable(el.props["mount_row"])
