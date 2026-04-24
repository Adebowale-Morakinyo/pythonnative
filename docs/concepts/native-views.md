# Native views

The reconciler doesn't know what a `Text` or a `Button` is. It only
knows how to call into a
[`ViewHandler`][pythonnative.native_views.base.ViewHandler]: create,
update, add child, remove child. The mapping from element types
(`"Text"`, `"Button"`, `"Column"`, ...) to handlers lives in the
[`NativeViewRegistry`][pythonnative.native_views.NativeViewRegistry].

This page describes that boundary, walks through what a handler
actually does on each platform, and covers the testing-mode mock
registry used by `pytest`.

## The handler protocol

Every native widget is implemented as a class that fulfils the
[`ViewHandler`][pythonnative.native_views.base.ViewHandler] protocol.
The five hot-path methods are:

| Method | When it's called |
|---|---|
| `create_view(props)` | Once, when the element first mounts. Returns a native view object. |
| `update_view(view, prev_props, next_props)` | On every commit where this element survives a diff. |
| `add_child(parent, child, index)` | When a new child appears in this slot. |
| `remove_child(parent, child)` | When a child is removed from this slot. |
| `insert_child(parent, child, index)` | When a child moves to a new slot (keyed reconciliation). |

The handler returns a native view object (a `UIView` on iOS, a
`android.view.View` on Android). The reconciler holds onto that handle
in its [`VNode`][pythonnative.reconciler.VNode] and passes it back to
the handler on subsequent calls.

```python
class MyHandler(ViewHandler):
    def create_view(self, props):
        v = NativeWidget()
        self.update_view(v, {}, props)
        return v

    def update_view(self, view, prev, next):
        if prev.get("text") != next.get("text"):
            view.setText(next.get("text", ""))
```

## The registry

The [`NativeViewRegistry`][pythonnative.native_views.NativeViewRegistry]
is a dict-like object that maps element type strings to handler
*instances*. The registry is selected lazily by platform:

- On Android, `pythonnative.native_views.android.register_handlers`
  populates the registry with Chaquopy-backed handlers.
- On iOS, `pythonnative.native_views.ios.register_handlers` does the
  same with rubicon-objc handlers.
- On the desktop (during tests), the registry is replaced with a mock
  via [`set_registry`][pythonnative.native_views.set_registry] before
  any element is rendered.

Custom widgets follow the same pattern: register a handler under a
unique type string, then construct elements with that type and the
reconciler will pick it up.

## Layout and styling

Both platform implementations agree on a small set of style keys:

- **Layout**: `width`, `height`, `flex`, `flex_grow`, `flex_shrink`,
  `min_width`, `max_width`, `min_height`, `max_height`, `align_self`.
- **Container**: `flex_direction`, `justify_content`, `align_items`,
  `spacing`, `padding`, `margin`, `overflow`.
- **Visual**: `background_color`, `border_*`, `corner_radius`,
  `font_size`, `font_family`, `bold`, `italic`, `text_align`, `color`.

The handler implementations translate these into:

- **iOS**: `NSLayoutConstraint`s on a `UIView`, `UIStackView` axis
  configuration for `Column`/`Row`, and `UILabel`/`UIButton`/`UIImage`
  property assignments for visuals.
- **Android**: `LinearLayout` orientation for `Column`/`Row`, padding
  in `dp` (computed from `Resources.getDisplayMetrics().density`), and
  direct property setters on `TextView`, `Button`, `ImageView`, etc.

A subset of layout keys are **container-only** (`flex_direction`,
`align_items`, `justify_content`, `spacing`) and another subset is
**child-only** (`flex`, `flex_grow`, `align_self`). Mixing them up is
silently ignored: the handler only consults the keys that apply.

## Children

Children of a container element become subviews of the corresponding
native view. The reconciler determines insertion order (and reorders
on key change), but the handler is responsible for the actual native
mutations:

- iOS containers use `addArrangedSubview:` /
  `insertArrangedSubview:atIndex:` on `UIStackView`.
- Android containers use `addView(child, index)` /
  `removeView(child)` on `LinearLayout`.

For non-container elements (e.g., `Image`), the registry simply doesn't
register `add_child` / `remove_child`, and the reconciler raises if
the user tries to nest children inside one.

## Testing without a device

Production handlers require Chaquopy (Android) or rubicon-objc (iOS),
neither of which is available on a developer laptop. The test suite
sidesteps this with a mock registry that records calls instead of
creating real widgets:

```python
from pythonnative.native_views import set_registry, NativeViewRegistry

class _MockHandler:
    def create_view(self, props): return {"props": props, "children": []}
    def update_view(self, v, p, n): v["props"] = n
    def add_child(self, p, c, i): p["children"].insert(i, c)
    def remove_child(self, p, c): p["children"].remove(c)
    def insert_child(self, p, c, i): p["children"].insert(i, c)

mock = NativeViewRegistry()
for ty in ("Text", "Button", "Column", "Row"):
    mock.register(ty, _MockHandler())
set_registry(mock)
```

After that, a render produces a tree of plain dicts that test code can
introspect.

## Custom widgets

Adding a widget is a three-step process:

1. Implement a handler subclass for each platform you support.
2. Register it under a unique type string.
3. Add a small Python factory that returns
   `Element(<type>, props, children)`.

```python
import pythonnative as pn
from pythonnative.element import Element
from pythonnative.native_views import get_registry

class _RatingHandler:
    def create_view(self, props):
        # platform-specific stars widget
        ...
    def update_view(self, view, prev, next):
        ...

get_registry().register("Rating", _RatingHandler())

def Rating(value: float, *, on_change=None, **kwargs):
    return Element("Rating", {"value": value, "on_change": on_change, **kwargs}, [])
```

The reconciler treats `Rating` like any other element after that.

## Next steps

- Browse the API: [Native views](../api/native_views.md).
- See how the reconciler drives handlers: [Reconciliation](reconciliation.md).
- Wrap a device API instead of a widget: [Native modules guide](../guides/native-modules.md).
