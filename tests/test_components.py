"""Unit tests for the built-in element-creating functions."""

from pythonnative.components import (
    ActivityIndicator,
    Button,
    Column,
    Image,
    ProgressBar,
    Row,
    ScrollView,
    Spacer,
    Switch,
    Text,
    TextInput,
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
