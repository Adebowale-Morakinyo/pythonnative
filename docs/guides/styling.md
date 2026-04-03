# Styling

Style properties are passed as keyword arguments to element functions. PythonNative also provides a `StyleSheet` utility for creating reusable styles and a theming system via context.

## Inline styles

Pass style props directly to components:

```python
pn.Text("Hello", color="#FF3366", font_size=24, bold=True)
pn.Button("Tap", background_color="#FF1E88E5", color="#FFFFFF")
pn.Column(pn.Text("Content"), background_color="#FFF5F5F5")
```

## StyleSheet

Create reusable named styles with `StyleSheet.create()`:

```python
import pythonnative as pn

styles = pn.StyleSheet.create(
    title={"font_size": 28, "bold": True, "color": "#333"},
    subtitle={"font_size": 14, "color": "#666"},
    container={"padding": 16, "spacing": 12, "alignment": "fill"},
)

# Apply with dict unpacking
pn.Text("Welcome", **styles["title"])
pn.Column(
    pn.Text("Subtitle", **styles["subtitle"]),
    **styles["container"],
)
```

### Composing styles

Merge multiple style dicts with `StyleSheet.compose()`:

```python
base = {"font_size": 16, "color": "#000"}
highlight = {"color": "#FF0000", "bold": True}
merged = pn.StyleSheet.compose(base, highlight)
# Result: {"font_size": 16, "color": "#FF0000", "bold": True}
```

### Flattening styles

Flatten a style or list of styles into a single dict:

```python
pn.StyleSheet.flatten([base, highlight])
pn.StyleSheet.flatten(None)  # returns {}
```

## Colors

Pass hex strings (`#RRGGBB` or `#AARRGGBB`) to color props:

```python
pn.Text("Hello", color="#FF3366")
pn.Button("Tap", background_color="#FF1E88E5", color="#FFFFFF")
```

## Text styling

`Text` and `Button` accept `font_size`, `color`, `bold`, and `text_align`:

```python
pn.Text("Title", font_size=24, bold=True, text_align="center")
pn.Text("Subtitle", font_size=14, color="#666666")
```

## Layout properties

All components support common layout properties:

```python
pn.Text("Fixed size", width=200, height=50)
pn.View(child, flex=1, margin=8)
pn.Column(items, margin={"horizontal": 16, "vertical": 8})
```

- `width`, `height` — fixed dimensions in dp (Android) / pt (iOS)
- `flex` — flex grow factor within Column/Row
- `margin` — outer spacing (int for all sides, or dict)
- `min_width`, `max_width`, `min_height`, `max_height` — size constraints
- `align_self` — override parent alignment

## Layout with Column and Row

`Column` (vertical) and `Row` (horizontal):

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

### Alignment

Cross-axis alignment: `"fill"`, `"center"`, `"leading"` / `"start"`, `"trailing"` / `"end"`.

## Theming

PythonNative includes a built-in theme context with light and dark themes:

```python
import pythonnative as pn
from pythonnative.style import DEFAULT_DARK_THEME

@pn.component
def themed_text(text: str = "") -> pn.Element:
    theme = pn.use_context(pn.ThemeContext)
    return pn.Text(text, color=theme["text_color"], font_size=theme["font_size"])

class MyPage(pn.Page):
    def render(self):
        return pn.Provider(pn.ThemeContext, DEFAULT_DARK_THEME,
            pn.Column(
                themed_text(text="Dark mode!"),
                spacing=8,
            )
        )
```

### Theme properties

Both light and dark themes include:

- `primary_color`, `secondary_color` — accent colors
- `background_color`, `surface_color` — background colors
- `text_color`, `text_secondary_color` — text colors
- `error_color`, `success_color`, `warning_color` — semantic colors
- `font_size`, `font_size_small`, `font_size_large`, `font_size_title` — typography
- `spacing`, `spacing_large` — layout spacing
- `border_radius` — corner rounding

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
