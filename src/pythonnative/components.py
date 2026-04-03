"""Built-in element-creating functions for declarative UI composition.

Each function returns an :class:`Element` describing a native UI widget.
These are pure data — no native views are created until the reconciler
mounts the element tree.

Layout properties (``width``, ``height``, ``flex``, ``margin``,
``min_width``, ``max_width``, ``min_height``, ``max_height``,
``align_self``) are supported by all components.
"""

from typing import Any, Callable, Dict, List, Optional, Union

from .element import Element

# ======================================================================
# Shared helpers
# ======================================================================

PaddingValue = Union[int, float, Dict[str, Union[int, float]]]
MarginValue = Union[int, float, Dict[str, Union[int, float]]]


def _filter_none(**kwargs: Any) -> Dict[str, Any]:
    """Return *kwargs* with ``None``-valued entries removed."""
    return {k: v for k, v in kwargs.items() if v is not None}


def _layout_props(
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    min_height: Optional[float] = None,
    max_height: Optional[float] = None,
    align_self: Optional[str] = None,
) -> Dict[str, Any]:
    """Collect common layout props into a dict (excluding Nones)."""
    return _filter_none(
        width=width,
        height=height,
        flex=flex,
        margin=margin,
        min_width=min_width,
        max_width=max_width,
        min_height=min_height,
        max_height=max_height,
        align_self=align_self,
    )


# ======================================================================
# Leaf components
# ======================================================================


def Text(
    text: str = "",
    *,
    font_size: Optional[float] = None,
    color: Optional[str] = None,
    bold: bool = False,
    text_align: Optional[str] = None,
    background_color: Optional[str] = None,
    max_lines: Optional[int] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    min_height: Optional[float] = None,
    max_height: Optional[float] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Display text."""
    props = _filter_none(
        text=text,
        font_size=font_size,
        color=color,
        bold=bold or None,
        text_align=text_align,
        background_color=background_color,
        max_lines=max_lines,
    )
    props.update(
        _layout_props(
            width=width,
            height=height,
            flex=flex,
            margin=margin,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            align_self=align_self,
        )
    )
    return Element("Text", props, [], key=key)


def Button(
    title: str = "",
    *,
    on_click: Optional[Callable[[], None]] = None,
    color: Optional[str] = None,
    background_color: Optional[str] = None,
    font_size: Optional[float] = None,
    enabled: bool = True,
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    min_height: Optional[float] = None,
    max_height: Optional[float] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Create a tappable button."""
    props: Dict[str, Any] = {"title": title}
    if on_click is not None:
        props["on_click"] = on_click
    if color is not None:
        props["color"] = color
    if background_color is not None:
        props["background_color"] = background_color
    if font_size is not None:
        props["font_size"] = font_size
    if not enabled:
        props["enabled"] = False
    props.update(
        _layout_props(
            width=width,
            height=height,
            flex=flex,
            margin=margin,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            align_self=align_self,
        )
    )
    return Element("Button", props, [], key=key)


def TextInput(
    *,
    value: str = "",
    placeholder: str = "",
    on_change: Optional[Callable[[str], None]] = None,
    secure: bool = False,
    font_size: Optional[float] = None,
    color: Optional[str] = None,
    background_color: Optional[str] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    min_height: Optional[float] = None,
    max_height: Optional[float] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Create a single-line text entry field."""
    props: Dict[str, Any] = {"value": value}
    if placeholder:
        props["placeholder"] = placeholder
    if on_change is not None:
        props["on_change"] = on_change
    if secure:
        props["secure"] = True
    if font_size is not None:
        props["font_size"] = font_size
    if color is not None:
        props["color"] = color
    if background_color is not None:
        props["background_color"] = background_color
    props.update(
        _layout_props(
            width=width,
            height=height,
            flex=flex,
            margin=margin,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            align_self=align_self,
        )
    )
    return Element("TextInput", props, [], key=key)


def Image(
    source: str = "",
    *,
    width: Optional[float] = None,
    height: Optional[float] = None,
    scale_type: Optional[str] = None,
    background_color: Optional[str] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    min_height: Optional[float] = None,
    max_height: Optional[float] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Display an image from a resource path or URL."""
    props = _filter_none(
        source=source or None,
        width=width,
        height=height,
        scale_type=scale_type,
        background_color=background_color,
    )
    props.update(
        _layout_props(
            flex=flex,
            margin=margin,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            align_self=align_self,
        )
    )
    return Element("Image", props, [], key=key)


def Switch(
    *,
    value: bool = False,
    on_change: Optional[Callable[[bool], None]] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Create a toggle switch."""
    props: Dict[str, Any] = {"value": value}
    if on_change is not None:
        props["on_change"] = on_change
    props.update(_layout_props(width=width, height=height, flex=flex, margin=margin, align_self=align_self))
    return Element("Switch", props, [], key=key)


def ProgressBar(
    *,
    value: float = 0.0,
    background_color: Optional[str] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Show determinate progress (0.0 – 1.0)."""
    props = _filter_none(value=value, background_color=background_color)
    props.update(_layout_props(width=width, height=height, flex=flex, margin=margin, align_self=align_self))
    return Element("ProgressBar", props, [], key=key)


def ActivityIndicator(
    *,
    animating: bool = True,
    width: Optional[float] = None,
    height: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Show an indeterminate loading spinner."""
    props: Dict[str, Any] = {"animating": animating}
    props.update(_layout_props(width=width, height=height, margin=margin, align_self=align_self))
    return Element("ActivityIndicator", props, [], key=key)


def WebView(
    *,
    url: str = "",
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Embed web content."""
    props: Dict[str, Any] = {}
    if url:
        props["url"] = url
    props.update(_layout_props(width=width, height=height, flex=flex, margin=margin, align_self=align_self))
    return Element("WebView", props, [], key=key)


def Spacer(
    *,
    size: Optional[float] = None,
    flex: Optional[float] = None,
    key: Optional[str] = None,
) -> Element:
    """Insert empty space with an optional fixed size."""
    props = _filter_none(size=size, flex=flex)
    return Element("Spacer", props, [], key=key)


# ======================================================================
# Container components
# ======================================================================


def Column(
    *children: Element,
    spacing: float = 0,
    padding: Optional[PaddingValue] = None,
    alignment: Optional[str] = None,
    background_color: Optional[str] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    min_height: Optional[float] = None,
    max_height: Optional[float] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Arrange children vertically."""
    props = _filter_none(
        spacing=spacing or None,
        padding=padding,
        alignment=alignment,
        background_color=background_color,
    )
    props.update(
        _layout_props(
            width=width,
            height=height,
            flex=flex,
            margin=margin,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            align_self=align_self,
        )
    )
    return Element("Column", props, list(children), key=key)


def Row(
    *children: Element,
    spacing: float = 0,
    padding: Optional[PaddingValue] = None,
    alignment: Optional[str] = None,
    background_color: Optional[str] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    min_height: Optional[float] = None,
    max_height: Optional[float] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Arrange children horizontally."""
    props = _filter_none(
        spacing=spacing or None,
        padding=padding,
        alignment=alignment,
        background_color=background_color,
    )
    props.update(
        _layout_props(
            width=width,
            height=height,
            flex=flex,
            margin=margin,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            align_self=align_self,
        )
    )
    return Element("Row", props, list(children), key=key)


def ScrollView(
    child: Optional[Element] = None,
    *,
    background_color: Optional[str] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Wrap a single child in a scrollable container."""
    children = [child] if child is not None else []
    props = _filter_none(background_color=background_color)
    props.update(_layout_props(width=width, height=height, flex=flex, margin=margin, align_self=align_self))
    return Element("ScrollView", props, children, key=key)


def View(
    *children: Element,
    background_color: Optional[str] = None,
    padding: Optional[PaddingValue] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    min_height: Optional[float] = None,
    max_height: Optional[float] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Generic container view (``UIView`` / ``android.view.View``)."""
    props = _filter_none(
        background_color=background_color,
        padding=padding,
    )
    props.update(
        _layout_props(
            width=width,
            height=height,
            flex=flex,
            margin=margin,
            min_width=min_width,
            max_width=max_width,
            min_height=min_height,
            max_height=max_height,
            align_self=align_self,
        )
    )
    return Element("View", props, list(children), key=key)


def SafeAreaView(
    *children: Element,
    background_color: Optional[str] = None,
    padding: Optional[PaddingValue] = None,
    key: Optional[str] = None,
) -> Element:
    """Container that respects safe area insets (notch, status bar)."""
    props = _filter_none(background_color=background_color, padding=padding)
    return Element("SafeAreaView", props, list(children), key=key)


def Modal(
    *children: Element,
    visible: bool = False,
    on_dismiss: Optional[Callable[[], None]] = None,
    title: Optional[str] = None,
    background_color: Optional[str] = None,
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
    if background_color is not None:
        props["background_color"] = background_color
    return Element("Modal", props, list(children), key=key)


def Slider(
    *,
    value: float = 0.0,
    min_value: float = 0.0,
    max_value: float = 1.0,
    on_change: Optional[Callable[[float], None]] = None,
    width: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    align_self: Optional[str] = None,
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
    props.update(_layout_props(width=width, margin=margin, align_self=align_self))
    return Element("Slider", props, [], key=key)


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
    background_color: Optional[str] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    flex: Optional[float] = None,
    margin: Optional[MarginValue] = None,
    align_self: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Scrollable list that renders items from *data* using *render_item*.

    Each item is rendered by calling ``render_item(item, index)``.  If
    ``key_extractor`` is provided, it is called as ``key_extractor(item, index)``
    to produce a stable key for each child element.  This enables the
    reconciler to preserve widget state across data changes.
    """
    items: List[Element] = []
    for i, item in enumerate(data or []):
        el = render_item(item, i) if render_item else Text(str(item))
        if key_extractor is not None:
            el = Element(el.type, el.props, el.children, key=key_extractor(item, i))
        items.append(el)

    inner = Column(*items, spacing=separator_height)
    sv_props = _filter_none(background_color=background_color)
    sv_props.update(_layout_props(width=width, height=height, flex=flex, margin=margin, align_self=align_self))
    return Element("ScrollView", sv_props, [inner], key=key)
