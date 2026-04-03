# Styling

Style properties are passed via the `style` prop as a dict (or list of dicts) to any element function. PythonNative also provides a `StyleSheet` utility for creating reusable styles and a theming system via context.

## Inline styles

Pass a `style` dict to components:

```python
pn.Text("Hello", style={"color": "#FF3366", "font_size": 24, "bold": True})
pn.Button("Tap", style={"background_color": "#FF1E88E5", "color": "#FFFFFF"})
pn.Column(pn.Text("Content"), style={"background_color": "#FFF5F5F5"})
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

pn.Text("Welcome", style=styles["title"])
pn.Column(
    pn.Text("Subtitle", style=styles["subtitle"]),
    style=styles["container"],
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

### Combining styles with a list

You can also pass a list of dicts to `style`. They are merged left-to-right:

```python
pn.Text("Highlighted", style=[base, highlight])
```

### Flattening styles

Flatten a style or list of styles into a single dict:

```python
pn.StyleSheet.flatten([base, highlight])
pn.StyleSheet.flatten(None)  # returns {}
```

## Colors

Pass hex strings (`#RRGGBB` or `#AARRGGBB`) to color properties inside `style`:

```python
pn.Text("Hello", style={"color": "#FF3366"})
pn.Button("Tap", style={"background_color": "#FF1E88E5", "color": "#FFFFFF"})
```

## Text styling

`Text` and `Button` accept `font_size`, `color`, `bold`, and `text_align` inside `style`:

```python
pn.Text("Title", style={"font_size": 24, "bold": True, "text_align": "center"})
pn.Text("Subtitle", style={"font_size": 14, "color": "#666666"})
```

## Layout properties

All components support common layout properties inside `style`:

```python
pn.Text("Fixed size", style={"width": 200, "height": 50})
pn.View(child, style={"flex": 1, "margin": 8})
pn.Column(items, style={"margin": {"horizontal": 16, "vertical": 8}})
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
    style={"spacing": 8, "padding": 16, "alignment": "fill"},
)
```

### Alignment properties

Column and Row support `align_items` and `justify_content` inside `style`:

- **`align_items`** — cross-axis alignment: `"fill"`, `"center"`, `"leading"` / `"start"`, `"trailing"` / `"end"`
- **`justify_content`** — main-axis distribution: `"start"`, `"center"`, `"end"`, `"space_between"`, `"space_around"`
- **`alignment`** — shorthand for cross-axis alignment (same values as `align_items`)

```python
pn.Row(
    pn.Text("Left"),
    pn.Spacer(flex=1),
    pn.Text("Right"),
    style={"align_items": "center", "justify_content": "space_between", "padding": 16},
)
```

### Spacing

- `spacing` sets the gap between children in dp (Android) / points (iOS).

### Padding

- `padding: 16` — all sides
- `padding: {"horizontal": 12, "vertical": 8}` — per axis
- `padding: {"left": 8, "top": 16, "right": 8, "bottom": 16}` — per side

## Theming

PythonNative includes a built-in theme context with light and dark themes:

```python
import pythonnative as pn
from pythonnative.style import DEFAULT_DARK_THEME


@pn.component
def ThemedText(text: str = ""):
    theme = pn.use_context(pn.ThemeContext)
    return pn.Text(text, style={"color": theme["text_color"], "font_size": theme["font_size"]})


@pn.component
def DarkPage():
    return pn.Provider(pn.ThemeContext, DEFAULT_DARK_THEME,
        pn.Column(
            ThemedText(text="Dark mode!"),
            style={"spacing": 8},
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
        style={"spacing": 8},
    )
)
```
