"""Built-in element-creating functions for declarative UI composition.

Each function returns an :class:`Element` describing a native UI widget.
These are pure data — no native views are created until the reconciler
mounts the element tree.

All visual and layout properties are passed via the ``style`` parameter,
which accepts a dict or a list of dicts (later entries override earlier).

Layout properties supported by all components::

    width, height, flex, margin, min_width, max_width, min_height,
    max_height, align_self

Container-specific layout properties (Column / Row)::

    spacing, padding, align_items, justify_content
"""

from typing import Any, Callable, Dict, List, Optional

from .element import Element
from .style import StyleValue, resolve_style

# ======================================================================
# Leaf components
# ======================================================================


def Text(
    text: str = "",
    *,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Display text.

    Style properties: ``font_size``, ``color``, ``bold``, ``text_align``,
    ``background_color``, ``max_lines``, plus common layout props.
    """
    props: Dict[str, Any] = {"text": text}
    props.update(resolve_style(style))
    return Element("Text", props, [], key=key)


def Button(
    title: str = "",
    *,
    on_click: Optional[Callable[[], None]] = None,
    enabled: bool = True,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Create a tappable button.

    Style properties: ``color``, ``background_color``, ``font_size``,
    plus common layout props.
    """
    props: Dict[str, Any] = {"title": title}
    if on_click is not None:
        props["on_click"] = on_click
    if not enabled:
        props["enabled"] = False
    props.update(resolve_style(style))
    return Element("Button", props, [], key=key)


def TextInput(
    *,
    value: str = "",
    placeholder: str = "",
    on_change: Optional[Callable[[str], None]] = None,
    secure: bool = False,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Create a single-line text entry field.

    Style properties: ``font_size``, ``color``, ``background_color``,
    plus common layout props.
    """
    props: Dict[str, Any] = {"value": value}
    if placeholder:
        props["placeholder"] = placeholder
    if on_change is not None:
        props["on_change"] = on_change
    if secure:
        props["secure"] = True
    props.update(resolve_style(style))
    return Element("TextInput", props, [], key=key)


def Image(
    source: str = "",
    *,
    scale_type: Optional[str] = None,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Display an image from a resource path or URL.

    Style properties: ``background_color``, plus common layout props.
    """
    props: Dict[str, Any] = {}
    if source:
        props["source"] = source
    if scale_type is not None:
        props["scale_type"] = scale_type
    props.update(resolve_style(style))
    return Element("Image", props, [], key=key)


def Switch(
    *,
    value: bool = False,
    on_change: Optional[Callable[[bool], None]] = None,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Create a toggle switch."""
    props: Dict[str, Any] = {"value": value}
    if on_change is not None:
        props["on_change"] = on_change
    props.update(resolve_style(style))
    return Element("Switch", props, [], key=key)


def ProgressBar(
    *,
    value: float = 0.0,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Show determinate progress (0.0 – 1.0)."""
    props: Dict[str, Any] = {"value": value}
    props.update(resolve_style(style))
    return Element("ProgressBar", props, [], key=key)


def ActivityIndicator(
    *,
    animating: bool = True,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Show an indeterminate loading spinner."""
    props: Dict[str, Any] = {"animating": animating}
    props.update(resolve_style(style))
    return Element("ActivityIndicator", props, [], key=key)


def WebView(
    *,
    url: str = "",
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Embed web content."""
    props: Dict[str, Any] = {}
    if url:
        props["url"] = url
    props.update(resolve_style(style))
    return Element("WebView", props, [], key=key)


def Spacer(
    *,
    size: Optional[float] = None,
    flex: Optional[float] = None,
    key: Optional[str] = None,
) -> Element:
    """Insert empty space with an optional fixed size or flex weight."""
    props: Dict[str, Any] = {}
    if size is not None:
        props["size"] = size
    if flex is not None:
        props["flex"] = flex
    return Element("Spacer", props, [], key=key)


def Slider(
    *,
    value: float = 0.0,
    min_value: float = 0.0,
    max_value: float = 1.0,
    on_change: Optional[Callable[[float], None]] = None,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Continuous value slider."""
    props: Dict[str, Any] = {
        "value": value,
        "min_value": min_value,
        "max_value": max_value,
    }
    if on_change is not None:
        props["on_change"] = on_change
    props.update(resolve_style(style))
    return Element("Slider", props, [], key=key)


# ======================================================================
# Container components
# ======================================================================


def Column(
    *children: Element,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Arrange children vertically.

    Style properties: ``spacing``, ``padding``, ``align_items``,
    ``justify_content``, ``background_color``, plus common layout props.

    ``align_items`` controls cross-axis (horizontal) alignment:
    ``"stretch"`` (default), ``"flex_start"``/``"leading"``,
    ``"center"``, ``"flex_end"``/``"trailing"``.

    ``justify_content`` controls main-axis (vertical) distribution:
    ``"flex_start"`` (default), ``"center"``, ``"flex_end"``,
    ``"space_between"``, ``"space_around"``, ``"space_evenly"``.
    """
    props: Dict[str, Any] = {}
    props.update(resolve_style(style))
    return Element("Column", props, list(children), key=key)


def Row(
    *children: Element,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Arrange children horizontally.

    Style properties: ``spacing``, ``padding``, ``align_items``,
    ``justify_content``, ``background_color``, plus common layout props.

    ``align_items`` controls cross-axis (vertical) alignment:
    ``"stretch"`` (default), ``"flex_start"``/``"top"``,
    ``"center"``, ``"flex_end"``/``"bottom"``.

    ``justify_content`` controls main-axis (horizontal) distribution:
    ``"flex_start"`` (default), ``"center"``, ``"flex_end"``,
    ``"space_between"``, ``"space_around"``, ``"space_evenly"``.
    """
    props: Dict[str, Any] = {}
    props.update(resolve_style(style))
    return Element("Row", props, list(children), key=key)


def ScrollView(
    child: Optional[Element] = None,
    *,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Wrap a single child in a scrollable container."""
    children = [child] if child is not None else []
    props: Dict[str, Any] = {}
    props.update(resolve_style(style))
    return Element("ScrollView", props, children, key=key)


def View(
    *children: Element,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Generic container view (``UIView`` / ``android.view.View``)."""
    props: Dict[str, Any] = {}
    props.update(resolve_style(style))
    return Element("View", props, list(children), key=key)


def SafeAreaView(
    *children: Element,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Container that respects safe area insets (notch, status bar)."""
    props: Dict[str, Any] = {}
    props.update(resolve_style(style))
    return Element("SafeAreaView", props, list(children), key=key)


def Modal(
    *children: Element,
    visible: bool = False,
    on_dismiss: Optional[Callable[[], None]] = None,
    title: Optional[str] = None,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Overlay modal dialog.

    The modal is shown when ``visible=True`` and hidden when ``False``.
    """
    props: Dict[str, Any] = {"visible": visible}
    if on_dismiss is not None:
        props["on_dismiss"] = on_dismiss
    if title is not None:
        props["title"] = title
    props.update(resolve_style(style))
    return Element("Modal", props, list(children), key=key)


def Pressable(
    child: Optional[Element] = None,
    *,
    on_press: Optional[Callable[[], None]] = None,
    on_long_press: Optional[Callable[[], None]] = None,
    key: Optional[str] = None,
) -> Element:
    """Wrapper that adds press handling to any child element."""
    props: Dict[str, Any] = {}
    if on_press is not None:
        props["on_press"] = on_press
    if on_long_press is not None:
        props["on_long_press"] = on_long_press
    children = [child] if child is not None else []
    return Element("Pressable", props, children, key=key)


def FlatList(
    *,
    data: Optional[List[Any]] = None,
    render_item: Optional[Callable[[Any, int], Element]] = None,
    key_extractor: Optional[Callable[[Any, int], str]] = None,
    separator_height: float = 0,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Scrollable list that renders items from *data* using *render_item*.

    Each item is rendered by calling ``render_item(item, index)``.  If
    ``key_extractor`` is provided, it is called as ``key_extractor(item, index)``
    to produce a stable key for each child element.
    """
    items: List[Element] = []
    for i, item in enumerate(data or []):
        el = render_item(item, i) if render_item else Text(str(item))
        if key_extractor is not None:
            el = Element(el.type, el.props, el.children, key=key_extractor(item, i))
        items.append(el)

    inner = Column(*items, style={"spacing": separator_height} if separator_height else None)
    sv_props: Dict[str, Any] = {}
    sv_props.update(resolve_style(style))
    return Element("ScrollView", sv_props, [inner], key=key)
