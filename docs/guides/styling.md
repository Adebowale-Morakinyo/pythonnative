# Styling

Style properties are passed as keyword arguments to element functions. This replaces the old fluent setter pattern.

## Colors

Pass hex strings (`#RRGGBB` or `#AARRGGBB`) to color props:

```python
pn.Text("Hello", color="#FF3366")
pn.Button("Tap", background_color="#FF1E88E5", color="#FFFFFF")
pn.Column(pn.Text("Content"), background_color="#FFF5F5F5")
```

## Text styling

`Text` and `Button` accept `font_size`, `color`, `bold`, and `text_align`:

```python
pn.Text("Title", font_size=24, bold=True, text_align="center")
pn.Text("Subtitle", font_size=14, color="#666666")
```

## Layout with Column and Row

`Column` (vertical) and `Row` (horizontal) replace the old `StackView`:

```python
pn.Column(
    pn.Text("Username"),
    pn.TextInput(placeholder="Enter username"),
    pn.Text("Password"),
    pn.TextInput(placeholder="Enter password", secure=True),
    pn.Button("Login", on_click=handle_login),
    spacing=8,
    padding=16,
    alignment="fill",
)
```

### Spacing

- `spacing=N` sets the gap between children in dp (Android) / points (iOS).

### Padding

- `padding=16` — all sides
- `padding={"horizontal": 12, "vertical": 8}` — per axis
- `padding={"left": 8, "top": 16, "right": 8, "bottom": 16}` — per side

Android: applied via `setPadding` in dp. iOS: best-effort via layout margins.

### Alignment

Cross-axis alignment: `"fill"`, `"center"`, `"leading"` / `"start"`, `"trailing"` / `"end"`.

## ScrollView

Wrap content in a `ScrollView`:

```python
pn.ScrollView(
    pn.Column(
        pn.Text("Item 1"),
        pn.Text("Item 2"),
        # ... many items
        spacing=8,
    )
)
```
