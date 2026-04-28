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
The hot-path methods are:

| Method | When it's called |
|---|---|
| `create_view(props)` | Once, when the element first mounts. Returns a native view object. |
| `update_view(view, prev_props, next_props)` | On every commit where this element survives a diff. |
| `add_child(parent, child, index)` | When a new child appears in this slot. |
| `remove_child(parent, child)` | When a child is removed from this slot. |
| `insert_child(parent, child, index)` | When a child moves to a new slot (keyed reconciliation). |
| `set_frame(view, x, y, width, height)` | After every commit, to apply the frame computed by `pythonnative.layout`. |
| `measure_intrinsic(view, max_w, max_h)` | Called by the layout engine on leaf widgets that need a content-derived size. |

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

    def set_frame(self, view, x, y, width, height):
        view.setFrame(x, y, width, height)

    def measure_intrinsic(self, view, max_w, max_h):
        size = view.measure(max_w, max_h)
        return (size.width, size.height)
```

Handlers do **not** read flex / margin / padding props themselves —
those are interpreted by `pythonnative.layout` and turned into
`set_frame` calls. A handler only needs to apply the frame it is
given.

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

Layout-related style keys are interpreted by the central
`pythonnative.layout` engine, *not* by the platform handlers. The
full list (sizing, flex, position, margin, padding, spacing, …) is
documented in [Component properties](../api/component-properties.md).
The set of keys the layout engine consumes is exposed as
`pythonnative.layout.LAYOUT_STYLE_KEYS`.

Handlers only deal with **visual** properties — colours, fonts,
borders, corner radii, image scaling, text content. The reconciler
splits each element's style into "layout-only" keys (forwarded to the
layout engine) and "visual" keys (forwarded to
`update_view`). After each commit the reconciler runs the layout pass
and calls `handler.set_frame(view, x, y, w, h)` for every node.

On each platform that boils down to:

- **iOS**: every container is a plain `UIView` with
  `translatesAutoresizingMaskIntoConstraints = NO`; `set_frame`
  assigns `view.frame = CGRect(x, y, w, h)`. Leaf widgets implement
  `measure_intrinsic` via `sizeThatFits_`. Visual props
  (`background_color`, `corner_radius`, `font_*`, `color`, `text_align`,
  …) are applied directly through UIKit setters.
- **Android**: every container is a plain `FrameLayout`; `set_frame`
  builds a `MarginLayoutParams` and sets `view.x` / `view.y`. Padding
  in `dp` is computed from `Resources.getDisplayMetrics().density`. Leaf
  widgets implement `measure_intrinsic` with `View.measure(...)` plus
  `MeasureSpec`. Visual props are applied through `setBackgroundColor`,
  `setTextColor`, `setTextSize`, etc.

Because layout is centralised, the same `style` dict produces the same
geometry on Android and iOS — there is no "container-only" vs
"child-only" trap to fall into.

## Children

Children of a container element become subviews of the corresponding
native view. The reconciler determines insertion order (and reorders
on key change), but the handler is responsible for the actual native
mutations:

- iOS containers use `addSubview_` and
  `insertSubview_atIndex_` on a plain `UIView`.
- Android containers use `addView(child, index)` /
  `removeView(child)` on a `FrameLayout`.

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
    def create_view(self, props):
        return {"props": props, "children": [], "frame": (0, 0, 0, 0)}

    def update_view(self, v, p, n):
        v["props"] = n

    def add_child(self, p, c, i):
        p["children"].insert(i, c)

    def remove_child(self, p, c):
        p["children"].remove(c)

    def insert_child(self, p, c, i):
        p["children"].insert(i, c)

    def set_frame(self, v, x, y, w, h):
        v["frame"] = (x, y, w, h)

    def measure_intrinsic(self, v, max_w, max_h):
        return (0.0, 0.0)

mock = NativeViewRegistry()
for ty in ("Text", "Button", "View", "Column", "Row"):
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
- Read the [Layout engine](layout.md) concept page to understand how
  `set_frame` calls are produced.
- See how the reconciler drives handlers: [Reconciliation](reconciliation.md).
- Wrap a device API instead of a widget: [Native modules guide](../guides/native-modules.md).
