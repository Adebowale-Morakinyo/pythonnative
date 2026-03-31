"""Built-in element-creating functions for declarative UI composition.

Each function returns an :class:`Element` describing a native UI widget.
These are pure data — no native views are created until the reconciler
mounts the element tree.

Naming follows React Native conventions:

- ``Text`` (was *Label*)
- ``Button``
- ``Column`` / ``Row`` (was *StackView* vertical/horizontal)
- ``ScrollView``
- ``TextInput`` (was *TextField*)
- ``Image`` (was *ImageView*)
- ``Switch``
- ``ProgressBar`` (was *ProgressView*)
- ``ActivityIndicator`` (was *ActivityIndicatorView*)
- ``WebView``
- ``Spacer`` (new)
"""

from typing import Any, Callable, Dict, Optional, Union

from .element import Element


def _filter_none(**kwargs: Any) -> Dict[str, Any]:
    """Return *kwargs* with ``None``-valued entries removed."""
    return {k: v for k, v in kwargs.items() if v is not None}


# ---------------------------------------------------------------------------
# Leaf components
# ---------------------------------------------------------------------------


def Text(
    text: str = "",
    *,
    font_size: Optional[float] = None,
    color: Optional[str] = None,
    bold: bool = False,
    text_align: Optional[str] = None,
    background_color: Optional[str] = None,
    max_lines: Optional[int] = None,
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
    return Element("Text", props, [], key=key)


def Button(
    title: str = "",
    *,
    on_click: Optional[Callable[[], None]] = None,
    color: Optional[str] = None,
    background_color: Optional[str] = None,
    font_size: Optional[float] = None,
    enabled: bool = True,
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
    return Element("TextInput", props, [], key=key)


def Image(
    source: str = "",
    *,
    width: Optional[float] = None,
    height: Optional[float] = None,
    scale_type: Optional[str] = None,
    background_color: Optional[str] = None,
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
    return Element("Image", props, [], key=key)


def Switch(
    *,
    value: bool = False,
    on_change: Optional[Callable[[bool], None]] = None,
    key: Optional[str] = None,
) -> Element:
    """Create a toggle switch."""
    props: Dict[str, Any] = {"value": value}
    if on_change is not None:
        props["on_change"] = on_change
    return Element("Switch", props, [], key=key)


def ProgressBar(
    *,
    value: float = 0.0,
    background_color: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Show determinate progress (0.0 – 1.0)."""
    props = _filter_none(value=value, background_color=background_color)
    return Element("ProgressBar", props, [], key=key)


def ActivityIndicator(
    *,
    animating: bool = True,
    key: Optional[str] = None,
) -> Element:
    """Show an indeterminate loading spinner."""
    return Element("ActivityIndicator", {"animating": animating}, [], key=key)


def WebView(
    *,
    url: str = "",
    key: Optional[str] = None,
) -> Element:
    """Embed web content."""
    props: Dict[str, Any] = {}
    if url:
        props["url"] = url
    return Element("WebView", props, [], key=key)


def Spacer(
    *,
    size: Optional[float] = None,
    key: Optional[str] = None,
) -> Element:
    """Insert empty space with an optional fixed size."""
    props = _filter_none(size=size)
    return Element("Spacer", props, [], key=key)


# ---------------------------------------------------------------------------
# Container components
# ---------------------------------------------------------------------------

PaddingValue = Union[int, float, Dict[str, Union[int, float]]]


def Column(
    *children: Element,
    spacing: float = 0,
    padding: Optional[PaddingValue] = None,
    alignment: Optional[str] = None,
    background_color: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Arrange children vertically."""
    props = _filter_none(
        spacing=spacing or None,
        padding=padding,
        alignment=alignment,
        background_color=background_color,
    )
    return Element("Column", props, list(children), key=key)


def Row(
    *children: Element,
    spacing: float = 0,
    padding: Optional[PaddingValue] = None,
    alignment: Optional[str] = None,
    background_color: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Arrange children horizontally."""
    props = _filter_none(
        spacing=spacing or None,
        padding=padding,
        alignment=alignment,
        background_color=background_color,
    )
    return Element("Row", props, list(children), key=key)


def ScrollView(
    child: Optional[Element] = None,
    *,
    background_color: Optional[str] = None,
    key: Optional[str] = None,
) -> Element:
    """Wrap a single child in a scrollable container."""
    children = [child] if child is not None else []
    props = _filter_none(background_color=background_color)
    return Element("ScrollView", props, children, key=key)
