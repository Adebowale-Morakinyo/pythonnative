## Component Property Reference (v0.4.0)

This page summarizes common properties and fluent setters added in v0.4.0. Unless noted, methods return `self` for chaining.

### View (base)

- `set_background_color(color)`
  - Accepts ARGB int or `#RRGGBB` / `#AARRGGBB` string.

- `set_padding(*, all=None, horizontal=None, vertical=None, left=None, top=None, right=None, bottom=None)`
  - Android: applies padding in dp.
  - iOS: currently a no-op for most views.

- `set_margin(*, all=None, horizontal=None, vertical=None, left=None, top=None, right=None, bottom=None)`
  - Android: applied when added to `StackView` (LinearLayout) as `LayoutParams` margins (dp).
  - iOS: not currently applied.

- `wrap_in_scroll()` → `ScrollView`
  - Returns a `ScrollView` containing this view.

### ScrollView

- `ScrollView.wrap(view)` → `ScrollView`
  - Class helper to wrap a single child.

### StackView

- `set_axis('vertical'|'horizontal')`
- `set_spacing(n)`
  - Android: dp via divider drawable.
  - iOS: `UIStackView.spacing` (points).
- `set_alignment('fill'|'center'|'leading'|'trailing'|'top'|'bottom')`
  - Cross-axis alignment; top/bottom map appropriately for horizontal stacks.

### Text components

Applies to `Label`, `TextField`, `TextView`:

- `set_text(text)`
- `set_text_color(color)`
- `set_text_size(size)`

Platform notes:
- Android: `setTextColor(int)`, `setTextSize(sp)`.
- iOS: `setTextColor(UIColor)`, `UIFont.systemFont(ofSize:)`.

### Button

- `set_title(text)`
- `set_on_click(callback)`


