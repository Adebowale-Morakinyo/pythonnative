## Styling

This guide covers the lightweight styling APIs introduced in v0.4.0.

The goal is to provide a small, predictable set of cross-platform styling hooks. Some features are Android-only today and will expand over time.

### Colors

- Use `set_background_color(color)` on any view.
- Color can be an ARGB int or a hex string like `#RRGGBB` or `#AARRGGBB`.

```python
stack = pn.StackView().set_background_color("#FFF5F5F5")
```

### Padding and Margin

- `set_padding(...)` is available on all views.
  - Android: applies using `View.setPadding` with dp units.
  - iOS: currently a no-op for most views; prefer container spacing (`StackView.set_spacing`) and layout.

- `set_margin(...)` records margins on the child view.
  - Android: applied automatically when added to a `StackView` (LinearLayout) via `LayoutParams.setMargins` (dp).
  - iOS: not currently applied.

`set_padding`/`set_margin` accept these parameters (integers): `all`, `horizontal`, `vertical`, `left`, `top`, `right`, `bottom`. Individual sides override group values.

```python
pn.Label("Name").set_margin(bottom=8)
pn.TextField().set_padding(horizontal=12, vertical=8)
```

### Text styling

Text components expose:
- `set_text(text) -> self`
- `set_text_color(color) -> self` (hex or ARGB int)
- `set_text_size(size) -> self` (sp on Android; pt on iOS via system font)

Applies to `Label`, `TextField`, and `TextView`.

```python
pn.Label("Hello").set_text_color("#FF3366").set_text_size(18)
```

### StackView layout

`StackView` (Android LinearLayout / iOS UIStackView) adds configuration helpers:

- `set_axis('vertical'|'horizontal') -> self`
- `set_spacing(n) -> self` (dp on Android; points on iOS)
- `set_alignment(value) -> self`
  - Cross-axis alignment. Supported values: `fill`, `center`, `leading`/`top`, `trailing`/`bottom`.

```python
form = (
    pn.StackView()
      .set_axis('vertical')
      .set_spacing(8)
      .set_alignment('fill')
      .set_padding(all=16)
)
form.add_view(pn.Label("Username").set_margin(bottom=4))
form.add_view(pn.TextField().set_padding(horizontal=12, vertical=8))
```

### Scroll helpers

Wrap any view in a `ScrollView` using either approach:

```python
scroll = pn.ScrollView.wrap(form)
# or
scroll = form.wrap_in_scroll()
```

Attach the scroll view as your page root:

```python
self.set_root_view(scroll)
```

### Fluent setters

Most setters now return `self` for chaining, e.g.:

```python
pn.Button("Tap me").set_on_click(lambda: print("hi")).set_padding(all=8)
```

Note: Where platform limitations exist, the methods are no-ops and still return `self`.


