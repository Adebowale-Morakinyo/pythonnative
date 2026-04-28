"""Built-in element factories for declarative UI composition.

Each function in this module returns an [`Element`][pythonnative.Element]
describing a native UI widget. Element factories are pure data: no
native views are created until the reconciler mounts the element tree.

All visual and layout properties are passed via the `style` parameter,
which accepts a dict or a list of dicts (later entries override
earlier ones; see [`resolve_style`][pythonnative.style.resolve_style]).

Layout properties supported by every component:

- `width`, `height`, `flex`, `flex_grow`, `flex_shrink`, `margin`,
  `min_width`, `max_width`, `min_height`, `max_height`, `align_self`.

Flex container properties (`View` / `Column` / `Row`):

- `flex_direction`, `justify_content`, `align_items`, `overflow`,
  `spacing`, `padding`.

[`View`][pythonnative.View] is the universal flex container (like React
Native's `View`). It defaults to `flex_direction: "column"`.
[`Column`][pythonnative.Column] and [`Row`][pythonnative.Row] are
convenience wrappers that fix the direction.

Example:
    ```python
    import pythonnative as pn

    pn.Column(
        pn.Text("Hello", style={"font_size": 18}),
        pn.Button("Tap", on_click=lambda: print("tapped")),
        style={"spacing": 12, "padding": 16},
    )
    ```
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
    """Display a string of text.

    Style properties: `font_size`, `color`, `bold`, `text_align`,
    `background_color`, `max_lines`, plus the common layout props.

    Args:
        text: Text content to display.
        style: Style dict (or list of dicts) controlling appearance and
            layout.
        key: Stable identity for keyed reconciliation in lists.

    Returns:
        An [`Element`][pythonnative.Element] of type `"Text"`.
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
    """Display a tappable button.

    Style properties: `color`, `background_color`, `font_size`, plus the
    common layout props.

    Args:
        title: Button label.
        on_click: Callback invoked when the user taps the button.
        enabled: When `False`, the button is disabled and cannot be
            tapped.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"Button"`.
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
    """Display a single-line text entry field.

    Style properties: `font_size`, `color`, `background_color`, plus the
    common layout props.

    Args:
        value: Current text content (controlled-input pattern).
        placeholder: Hint shown when `value` is empty.
        on_change: Callback invoked with the new string each keystroke.
        secure: When `True`, characters are masked (use for passwords).
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"TextInput"`.
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

    Style properties: `background_color`, plus the common layout props.

    Args:
        source: Image resource name or URL.
        scale_type: Platform-specific fit mode (e.g., `"fit"`, `"fill"`,
            `"center"`).
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"Image"`.
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
    """Display a toggle switch.

    Args:
        value: Current on/off state.
        on_change: Callback invoked with the new boolean state.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"Switch"`.
    """
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
    """Show determinate progress as a value between 0.0 and 1.0.

    For indeterminate progress, use
    [`ActivityIndicator`][pythonnative.ActivityIndicator] instead.

    Args:
        value: Fraction complete (clamped to `[0.0, 1.0]` by the
            platform handler).
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"ProgressBar"`.
    """
    props: Dict[str, Any] = {"value": value}
    props.update(resolve_style(style))
    return Element("ProgressBar", props, [], key=key)


def ActivityIndicator(
    *,
    animating: bool = True,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Show an indeterminate loading spinner.

    Args:
        animating: When `False`, the spinner is hidden.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type
        `"ActivityIndicator"`.
    """
    props: Dict[str, Any] = {"animating": animating}
    props.update(resolve_style(style))
    return Element("ActivityIndicator", props, [], key=key)


def WebView(
    *,
    url: str = "",
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Embed web content from a URL.

    Args:
        url: HTTP(S) URL to load.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"WebView"`.
    """
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
    """Insert empty space inside a flex container.

    Pass `size` for a fixed gap, or `flex` to expand and absorb
    remaining space.

    Args:
        size: Fixed gap in dp/pt along the parent's main axis.
        flex: Flex-grow weight; useful for pushing siblings to the
            opposite end of a [`Row`][pythonnative.Row] or
            [`Column`][pythonnative.Column].
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"Spacer"`.
    """
    props: Dict[str, Any] = {}
    if size is not None:
        # The layout engine sees ``width`` / ``height`` only, so a fixed
        # ``size`` is mirrored on both axes. Whichever axis the parent
        # container's ``flex_direction`` chooses as main becomes the
        # actual gap; the cross axis is constrained by the parent's
        # ``align_items`` (typically ``stretch``) anyway.
        props["size"] = size
        props["width"] = size
        props["height"] = size
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
    """Continuous-value slider between `min_value` and `max_value`.

    Args:
        value: Current slider value.
        min_value: Lower bound.
        max_value: Upper bound.
        on_change: Callback invoked with the new value as the user
            drags.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"Slider"`.
    """
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


def View(
    *children: Element,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Universal flex container (like React Native's `View`).

    Defaults to `flex_direction: "column"`. Override via `style`:

    ```python
    pn.View(child_a, child_b, style={"flex_direction": "row"})
    ```

    Flex container properties (inside `style`):

    - `flex_direction`: `"column"` (default), `"row"`,
      `"column_reverse"`, `"row_reverse"`.
    - `justify_content`: main-axis distribution. Accepts `"flex_start"`
      (default), `"center"`, `"flex_end"`, `"space_between"`,
      `"space_around"`, `"space_evenly"`.
    - `align_items`: cross-axis alignment. Accepts `"stretch"` (default),
      `"flex_start"`, `"center"`, `"flex_end"`.
    - `overflow`: `"visible"` (default) or `"hidden"`.
    - `spacing`, `padding`, `background_color`.

    Args:
        *children: Child elements rendered inside the container.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"View"`.
    """
    props: Dict[str, Any] = {"flex_direction": "column"}
    props.update(resolve_style(style))
    return Element("View", props, list(children), key=key)


def Column(
    *children: Element,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Arrange children vertically.

    Convenience wrapper around [`View`][pythonnative.View] with
    `flex_direction` fixed to `"column"`. Use `View` directly if you
    need to switch between row and column at runtime.

    Style properties: `spacing`, `padding`, `align_items`,
    `justify_content`, `background_color`, `overflow`, plus the common
    layout props.

    `align_items` controls cross-axis (horizontal) alignment:
    `"stretch"` (default), `"flex_start"` / `"leading"`, `"center"`, or
    `"flex_end"` / `"trailing"`.

    `justify_content` controls main-axis (vertical) distribution:
    `"flex_start"` (default), `"center"`, `"flex_end"`,
    `"space_between"`, `"space_around"`, `"space_evenly"`.

    Args:
        *children: Child elements stacked top to bottom.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"Column"`.
    """
    props: Dict[str, Any] = {"flex_direction": "column"}
    props.update(resolve_style(style))
    props["flex_direction"] = "column"
    return Element("Column", props, list(children), key=key)


def Row(
    *children: Element,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Arrange children horizontally.

    Convenience wrapper around [`View`][pythonnative.View] with
    `flex_direction` fixed to `"row"`. Use `View` directly if you need
    to switch between row and column at runtime.

    Style properties: `spacing`, `padding`, `align_items`,
    `justify_content`, `background_color`, `overflow`, plus the common
    layout props.

    `align_items` controls cross-axis (vertical) alignment:
    `"stretch"` (default), `"flex_start"` / `"top"`, `"center"`, or
    `"flex_end"` / `"bottom"`.

    `justify_content` controls main-axis (horizontal) distribution:
    `"flex_start"` (default), `"center"`, `"flex_end"`,
    `"space_between"`, `"space_around"`, `"space_evenly"`.

    Args:
        *children: Child elements arranged left to right.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"Row"`.
    """
    props: Dict[str, Any] = {"flex_direction": "row"}
    props.update(resolve_style(style))
    props["flex_direction"] = "row"
    return Element("Row", props, list(children), key=key)


def ScrollView(
    child: Optional[Element] = None,
    *,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Wrap a single child in a scrollable container.

    Args:
        child: The single child to scroll. Wrap multiple elements in a
            [`Column`][pythonnative.Column] or
            [`Row`][pythonnative.Row] first.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"ScrollView"`.
    """
    children = [child] if child is not None else []
    props: Dict[str, Any] = {}
    props.update(resolve_style(style))
    return Element("ScrollView", props, children, key=key)


def SafeAreaView(
    *children: Element,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Container that respects safe-area insets (notch, status bar, home indicator).

    Args:
        *children: Child elements that should avoid system UI overlays.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"SafeAreaView"`.
    """
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

    The modal is shown when `visible=True` and hidden when `False`.
    Drive `visible` from a hook so the parent component can dismiss
    the modal in response to user actions.

    Args:
        *children: Modal content.
        visible: Controls whether the modal is presented.
        on_dismiss: Callback invoked when the user dismisses the modal
            via system gesture (e.g., backdrop tap or back button).
        title: Optional title bar text.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"Modal"`.
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
    """Wrap any child element with tap and long-press handlers.

    Useful for making non-button elements (text, images, custom views)
    respond to user taps without altering their visual appearance.

    Args:
        child: The single element to make pressable.
        on_press: Callback invoked on a normal tap.
        on_long_press: Callback invoked on a sustained press.
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"Pressable"`.
    """
    props: Dict[str, Any] = {}
    if on_press is not None:
        props["on_press"] = on_press
    if on_long_press is not None:
        props["on_long_press"] = on_long_press
    children = [child] if child is not None else []
    return Element("Pressable", props, children, key=key)


def ErrorBoundary(
    child: Optional[Element] = None,
    *,
    fallback: Optional[Any] = None,
    key: Optional[str] = None,
) -> Element:
    """Catch render errors in `child` and display `fallback` instead.

    `fallback` may be an [`Element`][pythonnative.Element] or a callable
    that receives the exception and returns an `Element`. Useful for
    isolating risky subtrees so a single failure doesn't crash the page.

    Args:
        child: Subtree to wrap.
        fallback: Element to render when `child` raises during render,
            or a callable `fallback(err) -> Element`.
        key: Stable identity for keyed reconciliation.

    Returns:
        An [`Element`][pythonnative.Element] of type `"__ErrorBoundary__"`.

    Example:
        ```python
        import pythonnative as pn

        pn.ErrorBoundary(
            MyRiskyComponent(),
            fallback=lambda err: pn.Text(f"Error: {err}"),
        )
        ```
    """
    props: Dict[str, Any] = {}
    if fallback is not None:
        props["__fallback__"] = fallback
    children = [child] if child is not None else []
    return Element("__ErrorBoundary__", props, children, key=key)


def FlatList(
    *,
    data: Optional[List[Any]] = None,
    render_item: Optional[Callable[[Any, int], Element]] = None,
    key_extractor: Optional[Callable[[Any, int], str]] = None,
    separator_height: float = 0,
    style: StyleValue = None,
    key: Optional[str] = None,
) -> Element:
    """Scrollable list that renders items from `data` using `render_item`.

    Each item is rendered by calling `render_item(item, index)`. If
    `key_extractor` is provided, it is called as
    `key_extractor(item, index)` to produce a stable key for keyed
    reconciliation, which is essential for efficient updates when the
    list is reordered or partially mutated.

    Args:
        data: Iterable of arbitrary item values.
        render_item: Function called per item, returning an
            [`Element`][pythonnative.Element]. Defaults to wrapping each
            item in a [`Text`][pythonnative.Text].
        key_extractor: Function returning a stable key per item.
        separator_height: Vertical gap between items, in dp/pt.
        style: Style dict (or list of dicts).
        key: Stable identity for keyed reconciliation of the list itself.

    Returns:
        An [`Element`][pythonnative.Element] of type `"ScrollView"` (a
        column wrapped in a scroll container).

    Example:
        ```python
        import pythonnative as pn

        items = [{"id": 1, "name": "Apples"}, {"id": 2, "name": "Oranges"}]

        pn.FlatList(
            data=items,
            render_item=lambda item, _: pn.Text(item["name"]),
            key_extractor=lambda item, _: str(item["id"]),
            separator_height=4,
        )
        ```
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
