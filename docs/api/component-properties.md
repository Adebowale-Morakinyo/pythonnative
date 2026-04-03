# Component Property Reference

All visual and layout properties are passed via the `style` dict (or list of dicts) to element functions. Behavioural properties (callbacks, data, content) remain as keyword arguments.

## Common layout properties (inside `style`)

All components accept these layout properties in their `style` dict:

- `width` — fixed width in dp (Android) / pt (iOS)
- `height` — fixed height
- `flex` — flex grow factor within Column/Row
- `margin` — outer spacing (int, float, or dict with `horizontal`, `vertical`, `left`, `top`, `right`, `bottom`)
- `min_width`, `max_width` — width constraints
- `min_height`, `max_height` — height constraints
- `align_self` — override parent alignment (`"fill"`, `"center"`, etc.)
- `key` — stable identity for reconciliation (passed as a kwarg, not inside `style`)

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

- `*children` — child elements (positional)
- Style properties:
  - `spacing` — gap between children (dp / pt)
  - `padding` — inner padding (int for all sides, or dict with `horizontal`, `vertical`, `left`, `top`, `right`, `bottom`)
  - `alignment` — cross-axis alignment shorthand
  - `align_items` — cross-axis alignment: `"fill"`, `"center"`, `"leading"` / `"start"`, `"trailing"` / `"end"`, `"stretch"`
  - `justify_content` — main-axis distribution: `"start"`, `"center"`, `"end"`, `"space_between"`, `"space_around"`
  - `background_color` — container background

## View

```python
pn.View(*children, style={"background_color": "#F5F5F5", "padding": 16})
```

Generic container (UIView / FrameLayout). Supports all layout properties in `style`.

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

## FlatList

```python
pn.FlatList(data=items, render_item=render_fn, key_extractor=key_fn,
            separator_height=1, style={"background_color": "#FFF"})
```

- `data` — list of items
- `render_item` — `(item, index) -> Element` function
- `key_extractor` — `(item, index) -> str` for stable keys
- `separator_height` — spacing between items
