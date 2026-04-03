# Component Property Reference

All style and behaviour properties are passed as keyword arguments to element functions.

## Common layout properties

All components accept these layout properties:

- `width` — fixed width in dp (Android) / pt (iOS)
- `height` — fixed height
- `flex` — flex grow factor within Column/Row
- `margin` — outer spacing (int, float, or dict with `horizontal`, `vertical`, `left`, `top`, `right`, `bottom`)
- `min_width`, `max_width` — width constraints
- `min_height`, `max_height` — height constraints
- `align_self` — override parent alignment (`"fill"`, `"center"`, etc.)
- `key` — stable identity for reconciliation

## Text

```python
pn.Text(text, font_size=None, color=None, bold=False, text_align=None,
        background_color=None, max_lines=None)
```

- `text` — display string
- `font_size` — size in sp (Android) / pt (iOS)
- `color` — text colour (`#RRGGBB` or `#AARRGGBB`)
- `bold` — bold weight
- `text_align` — `"left"`, `"center"`, or `"right"`
- `background_color` — view background
- `max_lines` — limit visible lines

## Button

```python
pn.Button(title, on_click=None, color=None, background_color=None,
          font_size=None, enabled=True)
```

- `title` — button label
- `on_click` — callback `() -> None`
- `color` — title text colour
- `background_color` — button background
- `enabled` — interactive state

## Column / Row

```python
pn.Column(*children, spacing=0, padding=None, alignment=None, background_color=None)
pn.Row(*children, spacing=0, padding=None, alignment=None, background_color=None)
```

- `spacing` — gap between children (dp / pt)
- `padding` — inner padding (int for all sides, or dict with `horizontal`, `vertical`, `left`, `top`, `right`, `bottom`)
- `alignment` — cross-axis: `"fill"`, `"center"`, `"leading"`, `"trailing"`, `"start"`, `"end"`, `"top"`, `"bottom"`
- `background_color` — container background

## View

```python
pn.View(*children, background_color=None, padding=None)
```

Generic container (UIView / FrameLayout). Supports all layout properties.

## SafeAreaView

```python
pn.SafeAreaView(*children, background_color=None, padding=None)
```

Container that respects safe area insets (notch, status bar).

## ScrollView

```python
pn.ScrollView(child, background_color=None)
```

## TextInput

```python
pn.TextInput(value="", placeholder="", on_change=None, secure=False,
             font_size=None, color=None, background_color=None)
```

- `on_change` — callback `(str) -> None` receiving new text

## Image

```python
pn.Image(source="", width=None, height=None, scale_type=None, background_color=None)
```

- `source` — image URL (`http://...` / `https://...`) or local resource name
- `scale_type` — `"cover"`, `"contain"`, `"stretch"`, `"center"`

## Switch

```python
pn.Switch(value=False, on_change=None)
```

- `on_change` — callback `(bool) -> None`

## Slider

```python
pn.Slider(value=0.0, min_value=0.0, max_value=1.0, on_change=None)
```

- `on_change` — callback `(float) -> None`

## ProgressBar

```python
pn.ProgressBar(value=0.0, background_color=None)
```

- `value` — 0.0 to 1.0

## ActivityIndicator

```python
pn.ActivityIndicator(animating=True)
```

## WebView

```python
pn.WebView(url="")
```

## Spacer

```python
pn.Spacer(size=None, flex=None)
```

- `size` — fixed dimension in dp / pt
- `flex` — flex grow factor

## Pressable

```python
pn.Pressable(child, on_press=None, on_long_press=None)
```

Wraps any child element with tap/long-press handling.

## Modal

```python
pn.Modal(*children, visible=False, on_dismiss=None, title=None, background_color=None)
```

Overlay dialog shown when `visible=True`.

## FlatList

```python
pn.FlatList(data=None, render_item=None, key_extractor=None,
            separator_height=0, background_color=None)
```

- `data` — list of items
- `render_item` — `(item, index) -> Element` function
- `key_extractor` — `(item, index) -> str` for stable keys
- `separator_height` — spacing between items
