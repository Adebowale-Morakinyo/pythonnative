"""Unit tests for the built-in element-creating functions."""

from pythonnative.components import (
    ActivityIndicator,
    Button,
    Column,
    FlatList,
    Image,
    Modal,
    Pressable,
    ProgressBar,
    Row,
    SafeAreaView,
    ScrollView,
    Slider,
    Spacer,
    Switch,
    Text,
    TextInput,
    View,
    WebView,
)

# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------


def test_text_defaults() -> None:
    el = Text()
    assert el.type == "Text"
    assert el.props.get("text", "") == ""
    assert el.children == []


def test_text_with_props() -> None:
    el = Text("Hello", font_size=18, color="#FF0000", bold=True, text_align="center")
    assert el.props["text"] == "Hello"
    assert el.props["font_size"] == 18
    assert el.props["color"] == "#FF0000"
    assert el.props["bold"] is True
    assert el.props["text_align"] == "center"


def test_text_none_props_excluded() -> None:
    el = Text("Hi")
    assert "font_size" not in el.props
    assert "color" not in el.props


def test_text_layout_props() -> None:
    el = Text("Hi", width=100, height=50, flex=1, margin=8, align_self="center")
    assert el.props["width"] == 100
    assert el.props["height"] == 50
    assert el.props["flex"] == 1
    assert el.props["margin"] == 8
    assert el.props["align_self"] == "center"


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------


def test_button_defaults() -> None:
    el = Button()
    assert el.type == "Button"
    assert el.props["title"] == ""
    assert "on_click" not in el.props


def test_button_with_callback() -> None:
    cb = lambda: None  # noqa: E731
    el = Button("Tap", on_click=cb, background_color="#123456")
    assert el.props["title"] == "Tap"
    assert el.props["on_click"] is cb
    assert el.props["background_color"] == "#123456"


def test_button_disabled() -> None:
    el = Button("Off", enabled=False)
    assert el.props["enabled"] is False


# ---------------------------------------------------------------------------
# Column / Row
# ---------------------------------------------------------------------------


def test_column_with_children() -> None:
    el = Column(Text("a"), Text("b"), spacing=10, padding=16, alignment="fill")
    assert el.type == "Column"
    assert len(el.children) == 2
    assert el.props["spacing"] == 10
    assert el.props["padding"] == 16
    assert el.props["alignment"] == "fill"


def test_row_with_children() -> None:
    el = Row(Text("x"), Text("y"), spacing=5)
    assert el.type == "Row"
    assert len(el.children) == 2
    assert el.props["spacing"] == 5


def test_column_no_spacing_omitted() -> None:
    el = Column()
    assert "spacing" not in el.props


def test_column_layout_props() -> None:
    el = Column(flex=2, margin={"horizontal": 8})
    assert el.props["flex"] == 2
    assert el.props["margin"] == {"horizontal": 8}


# ---------------------------------------------------------------------------
# ScrollView
# ---------------------------------------------------------------------------


def test_scrollview_with_child() -> None:
    child = Column(Text("a"))
    el = ScrollView(child)
    assert el.type == "ScrollView"
    assert len(el.children) == 1
    assert el.children[0] is child


def test_scrollview_empty() -> None:
    el = ScrollView()
    assert el.children == []


# ---------------------------------------------------------------------------
# TextInput
# ---------------------------------------------------------------------------


def test_textinput_defaults() -> None:
    el = TextInput()
    assert el.type == "TextInput"
    assert el.props["value"] == ""


def test_textinput_with_props() -> None:
    cb = lambda s: None  # noqa: E731
    el = TextInput(value="hi", placeholder="type...", on_change=cb, secure=True)
    assert el.props["value"] == "hi"
    assert el.props["placeholder"] == "type..."
    assert el.props["on_change"] is cb
    assert el.props["secure"] is True


# ---------------------------------------------------------------------------
# Other leaf components
# ---------------------------------------------------------------------------


def test_image() -> None:
    el = Image("icon.png", width=48, height=48)
    assert el.type == "Image"
    assert el.props["source"] == "icon.png"
    assert el.props["width"] == 48


def test_switch() -> None:
    el = Switch(value=True)
    assert el.type == "Switch"
    assert el.props["value"] is True


def test_progress_bar() -> None:
    el = ProgressBar(value=0.5)
    assert el.type == "ProgressBar"
    assert el.props["value"] == 0.5


def test_activity_indicator() -> None:
    el = ActivityIndicator(animating=False)
    assert el.type == "ActivityIndicator"
    assert el.props["animating"] is False


def test_webview() -> None:
    el = WebView(url="https://example.com")
    assert el.type == "WebView"
    assert el.props["url"] == "https://example.com"


def test_spacer() -> None:
    el = Spacer(size=20)
    assert el.type == "Spacer"
    assert el.props["size"] == 20


def test_spacer_empty() -> None:
    el = Spacer()
    assert el.type == "Spacer"
    assert el.props == {}


# ---------------------------------------------------------------------------
# Key support
# ---------------------------------------------------------------------------


def test_key_propagation() -> None:
    el = Text("keyed", key="k1")
    assert el.key == "k1"


def test_column_key() -> None:
    el = Column(key="col-1")
    assert el.key == "col-1"


# ---------------------------------------------------------------------------
# New components
# ---------------------------------------------------------------------------


def test_view_container() -> None:
    child = Text("inside")
    el = View(child, background_color="#FFF", padding=8, width=200)
    assert el.type == "View"
    assert len(el.children) == 1
    assert el.props["background_color"] == "#FFF"
    assert el.props["padding"] == 8
    assert el.props["width"] == 200


def test_safe_area_view() -> None:
    el = SafeAreaView(Text("safe"), background_color="#000")
    assert el.type == "SafeAreaView"
    assert len(el.children) == 1


def test_modal() -> None:
    cb = lambda: None  # noqa: E731
    el = Modal(Text("content"), visible=True, on_dismiss=cb, title="Alert")
    assert el.type == "Modal"
    assert el.props["visible"] is True
    assert el.props["on_dismiss"] is cb
    assert el.props["title"] == "Alert"
    assert len(el.children) == 1


def test_slider() -> None:
    cb = lambda v: None  # noqa: E731
    el = Slider(value=0.5, min_value=0, max_value=10, on_change=cb)
    assert el.type == "Slider"
    assert el.props["value"] == 0.5
    assert el.props["min_value"] == 0
    assert el.props["max_value"] == 10
    assert el.props["on_change"] is cb


def test_pressable() -> None:
    cb = lambda: None  # noqa: E731
    child = Text("tap me")
    el = Pressable(child, on_press=cb)
    assert el.type == "Pressable"
    assert el.props["on_press"] is cb
    assert len(el.children) == 1


def test_flat_list_basic() -> None:
    el = FlatList(
        data=["a", "b", "c"],
        render_item=lambda item, i: Text(item),
    )
    assert el.type == "ScrollView"
    assert len(el.children) == 1
    inner = el.children[0]
    assert inner.type == "Column"
    assert len(inner.children) == 3
    assert inner.children[0].props["text"] == "a"


def test_flat_list_with_keys() -> None:
    el = FlatList(
        data=[{"id": "x", "name": "X"}, {"id": "y", "name": "Y"}],
        render_item=lambda item, i: Text(item["name"]),
        key_extractor=lambda item, i: item["id"],
    )
    inner = el.children[0]
    assert inner.children[0].key == "x"
    assert inner.children[1].key == "y"


def test_flat_list_empty() -> None:
    el = FlatList(data=[], render_item=lambda item, i: Text(str(item)))
    inner = el.children[0]
    assert len(inner.children) == 0


def test_spacer_flex() -> None:
    el = Spacer(flex=1)
    assert el.props["flex"] == 1
