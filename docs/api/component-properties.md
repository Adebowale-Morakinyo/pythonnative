# Component Property Reference

All visual and layout properties are passed via the `style` dict (or list of dicts) to element functions. Behavioural properties (callbacks, data, content) remain as keyword arguments.

> Layout is computed by PythonNative's pure-Python flexbox engine (see
> [Layout engine](../concepts/layout.md)). The same `style` keys produce the
> same frames on Android and iOS — every property listed below is honoured by
> the engine and applied via `set_frame` on the underlying native view.

## Common layout properties (inside `style`)

All components accept these layout properties in their `style` dict:

### Sizing

- `width` — fixed width in dp (Android) / pt (iOS). Accepts an `int`/`float`,
  or a percentage string like `"50%"` (resolved against the parent's content
  width).
- `height` — fixed height. Same number / percentage rules as `width`.
- `min_width`, `max_width` — width constraints (numbers or `"%"` strings).
- `min_height`, `max_height` — height constraints.
- `aspect_ratio` — width / height ratio. When only one of `width` / `height`
  is known, the other axis is derived from this ratio.

### Flex

- `flex` — shorthand. Setting `flex: N` is equivalent to
  `flex_grow: N, flex_shrink: 1, flex_basis: 0`.
- `flex_grow` — how much a child grows to fill remaining main-axis space.
- `flex_shrink` — how much a child shrinks when its parent runs out of space.
- `flex_basis` — initial main-axis size before grow / shrink is applied
  (`"auto"`, a number, or a percentage string).
- `align_self` — override parent alignment for this child (`"auto"`,
  `"stretch"`, `"flex_start"`, `"center"`, `"flex_end"`).

### Spacing

- `margin` — outer spacing. Accepts a number (all sides), or a dict with any
  of `horizontal`, `vertical`, `left`, `top`, `right`, `bottom`.
- `padding` — inner spacing on container elements. Same shape as `margin`.
- `spacing` — gap between children of a flex container (applied along the
  main axis).
- `gap` — alias for `spacing`.

### Position

- `position` — `"relative"` (default) or `"absolute"`. Absolute children are
  removed from the normal flow and placed using `top` / `right` / `bottom` /
  `left` (numbers or percentage strings).
- `top`, `right`, `bottom`, `left` — offsets used when `position: "absolute"`.

### Other

- `key` — stable identity for reconciliation (passed as a kwarg, not inside
  `style`).

## View

```python
pn.View(*children, style={
    "flex_direction": "column",
    "justify_content": "center",
    "align_items": "center",
    "overflow": "hidden",
    "spacing": 8,
    "padding": 16,
    "background_color": "#F5F5F5",
})
```

Universal flex container (like React Native's `View`). Defaults to `flex_direction: "column"`.

Flex container properties (inside `style`):

- `flex_direction` — `"column"` (default), `"row"`, `"column_reverse"`, `"row_reverse"`
- `justify_content` — `"flex_start"`, `"center"`, `"flex_end"`, `"space_between"`, `"space_around"`, `"space_evenly"`
- `align_items` — `"stretch"`, `"flex_start"`, `"center"`, `"flex_end"`
- `overflow` — `"visible"` (default), `"hidden"`
- `spacing`, `padding`, `background_color`

Containers also fully support absolute positioning for their children:

```python
pn.View(
    pn.View(style={"position": "absolute", "top": 0, "left": 0,
                   "width": 40, "height": 40, "background_color": "#F00"}),
    pn.View(style={"position": "absolute", "bottom": 8, "right": 8,
                   "width": 40, "height": 40, "background_color": "#0A0"}),
    style={"width": 200, "height": 200, "background_color": "#EEE"},
)
```

## Text

```python
pn.Text(text, style={"font_size": 18, "color": "#333", "bold": True, "text_align": "center"})
```

- `text` — display string (positional)
- Style properties: `font_size`, `color`, `bold`, `text_align`, `background_color`, `max_lines`

## Button

```python
pn.Button(title, on_click=handler, style={"color": "#FFF", "background_color": "#007AFF", "font_size": 16})
```

- `title` — button label (positional)
- `on_click` — callback `() -> None`
- `enabled` — interactive state (kwarg, default `True`)
- Style properties: `color`, `background_color`, `font_size`

## Column / Row

```python
pn.Column(*children, style={"spacing": 12, "padding": 16, "align_items": "center"})
pn.Row(*children, style={"spacing": 8, "justify_content": "space_between"})
```

Convenience wrappers for `View` with fixed `flex_direction`:

- `Column` = `View` with `flex_direction: "column"` (always vertical)
- `Row` = `View` with `flex_direction: "row"` (always horizontal)

- `*children` — child elements (positional)
- Style properties:
  - `spacing` — gap between children (dp / pt)
  - `padding` — inner padding (int for all sides, or dict with `horizontal`, `vertical`, `left`, `top`, `right`, `bottom`)
  - `align_items` — cross-axis alignment: `"stretch"`, `"flex_start"`, `"center"`, `"flex_end"`, `"leading"`, `"trailing"`
  - `justify_content` — main-axis distribution: `"flex_start"`, `"center"`, `"flex_end"`, `"space_between"`, `"space_around"`, `"space_evenly"`
  - `overflow` — `"visible"` (default), `"hidden"`
  - `background_color` — container background

## SafeAreaView

```python
pn.SafeAreaView(*children, style={"background_color": "#FFF", "padding": 8})
```

Container that respects safe area insets (notch, status bar).

## ScrollView

```python
pn.ScrollView(child, style={"background_color": "#FFF"})
```

## TextInput

```python
pn.TextInput(value="", placeholder="Enter text", on_change=handler, secure=False,
             style={"font_size": 16, "color": "#000", "background_color": "#FFF"})
```

- `on_change` — callback `(str) -> None` receiving new text

## Image

```python
pn.Image(source="https://example.com/photo.jpg", style={"width": 200, "height": 150, "scale_type": "cover"})
```

- `source` — image URL (`http://...` / `https://...`) or local resource name
- Style properties: `width`, `height`, `scale_type` (`"cover"`, `"contain"`, `"stretch"`, `"center"`), `background_color`

## Switch

```python
pn.Switch(value=False, on_change=handler)
```

- `on_change` — callback `(bool) -> None`

## Slider

```python
pn.Slider(value=0.5, min_value=0.0, max_value=1.0, on_change=handler)
```

- `on_change` — callback `(float) -> None`

## ProgressBar

```python
pn.ProgressBar(value=0.5, style={"background_color": "#EEE"})
```

- `value` — 0.0 to 1.0

## ActivityIndicator

```python
pn.ActivityIndicator(animating=True)
```

## WebView

```python
pn.WebView(url="https://example.com")
```

## Spacer

```python
pn.Spacer(size=16, flex=1)
```

- `size` — fixed dimension in dp / pt
- `flex` — flex grow factor

## Pressable

```python
pn.Pressable(child, on_press=handler, on_long_press=handler)
```

Wraps any child element with tap/long-press handling.

## Modal

```python
pn.Modal(*children, visible=show_modal, on_dismiss=handler, title="Confirm",
         style={"background_color": "#FFF"})
```

Overlay dialog shown when `visible=True`.

## TabBar

```python
pn.Element("TabBar", {
    "items": [
        {"name": "Home", "title": "Home"},
        {"name": "Settings", "title": "Settings"},
    ],
    "active_tab": "Home",
    "on_tab_select": handler,
})
```

Native tab bar — typically created automatically by `Tab.Navigator`.

| Platform | Native view              |
|----------|--------------------------|
| Android  | `BottomNavigationView`   |
| iOS      | `UITabBar`               |

- `items` — list of `{"name": str, "title": str}` dicts defining each tab
- `active_tab` — the `name` of the currently active tab
- `on_tab_select` — callback `(str) -> None` receiving the selected tab name

## FlatList

```python
pn.FlatList(data=items, render_item=render_fn, key_extractor=key_fn,
            separator_height=1, style={"background_color": "#FFF"})
```

- `data` — list of items
- `render_item` — `(item, index) -> Element` function
- `key_extractor` — `(item, index) -> str` for stable keys
- `separator_height` — spacing between items
