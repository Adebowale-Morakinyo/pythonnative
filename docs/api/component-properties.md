# Component Property Reference

All style and behaviour properties are passed as keyword arguments to element functions.

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

## Switch

```python
pn.Switch(value=False, on_change=None)
```

- `on_change` — callback `(bool) -> None`

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
pn.Spacer(size=None)
```

- `size` — fixed dimension in dp / pt
