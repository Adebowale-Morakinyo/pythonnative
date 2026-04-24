# Architecture

PythonNative combines **direct native bindings** with a **declarative
reconciler**, giving you React-like ergonomics while calling native
platform APIs synchronously from Python.

## High-level model

1. **Declarative element tree.** Your `@pn.component` function returns
   a tree of [`Element`][pythonnative.Element] descriptors (similar to
   React elements / virtual DOM nodes).
2. **Function components and hooks.** All UI is built with
   `@pn.component` functions using
   [`use_state`][pythonnative.use_state],
   [`use_reducer`][pythonnative.use_reducer],
   [`use_effect`][pythonnative.use_effect],
   [`use_navigation`][pythonnative.use_navigation], and friends. The
   API is inspired by React hooks but designed for Python.
3. **Reconciler.** On first render, the
   [`Reconciler`][pythonnative.reconciler.Reconciler] walks the tree
   and creates real native views via the platform backend. On
   subsequent renders (triggered by hook state changes), it diffs the
   new tree against the previous one and applies the minimal set of
   native mutations.
4. **Post-render effects.** Effects queued via
   [`use_effect`][pythonnative.use_effect] are flushed **after** the
   reconciler commits native mutations, matching React semantics.
   This guarantees that effect callbacks interact with the committed
   native tree.
5. **State batching.** Multiple state updates triggered during a
   render pass (e.g., from effects) are automatically batched into a
   single re-render. Explicit batching is available via
   [`batch_updates`][pythonnative.batch_updates].
6. **Key-based reconciliation.** Children can be assigned stable
   `key` values to preserve identity across re-renders, which is
   critical for lists and dynamic content.
7. **Error boundaries.**
   [`ErrorBoundary`][pythonnative.ErrorBoundary] catches render
   errors in child subtrees and displays fallback UI, preventing a
   single component failure from crashing the entire page.
8. **Direct bindings.** Under the hood, native views are created and
   updated through direct platform calls:
   - **iOS**: rubicon-objc exposes Objective-C/Swift classes
     (`UILabel`, `UIButton`, `UIStackView`, etc.).
   - **Android**: Chaquopy exposes Java classes
     (`android.widget.TextView`, `android.widget.Button`, etc.) via
     the JNI bridge.
9. **Thin native bootstrap.** The host app remains native (Android
   `Activity` or iOS `UIViewController`). It calls
   [`create_page`][pythonnative.create_page] internally to bootstrap
   your Python component, and the reconciler drives the UI from
   there.

## How it works

```text
@pn.component fn   --->   Element tree   --->   Reconciler   --->   Native views
        ^                                            |
        |                                            v
   set_state()   <---------   schedule re-render   batched   --->   diff + patch
                                                                          |
                                                                          v
                                                                     flush effects
```

The reconciler uses **key-based diffing**: children are matched by
key first and by position only as a fallback. When a child with the
same key and type is found, its props are updated in place on the
native view. When the type changes, the old native view is destroyed
and a new one is created.

### Render lifecycle

1. **Render phase**: component functions execute. Hooks record state
   reads, queue effects, and register memos. No native mutations
   happen yet.
2. **Commit phase**: the reconciler applies the diff to native views,
   creating, updating, and removing views as needed.
3. **Effect phase**: pending effects are flushed in depth-first order
   (children before parents). Cleanup functions from the previous
   render run before new effect callbacks.
4. **Drain phase**: if effects set state, a new render pass is
   automatically triggered and the cycle repeats (up to a safety
   limit to prevent infinite loops).

See [Lifecycle](lifecycle.md) for a detailed walkthrough.

## Component model

PythonNative uses a single component model: **function components**
decorated with `@pn.component`.

```python
@pn.component
def Counter(initial: int = 0):
    count, set_count = pn.use_state(initial)
    return pn.Column(
        pn.Text(f"Count: {count}", style={"font_size": 18}),
        pn.Button("+", on_click=lambda: set_count(count + 1)),
        style={"spacing": 4},
    )
```

Each component is a Python function that:

- Accepts props as keyword arguments.
- Uses hooks for state ([`use_state`][pythonnative.use_state],
  [`use_reducer`][pythonnative.use_reducer]), side effects
  ([`use_effect`][pythonnative.use_effect]), navigation
  ([`use_navigation`][pythonnative.use_navigation]), and more.
- Returns an [`Element`][pythonnative.Element] tree describing the
  UI.
- Has its own hook state per call site (each instance gets its own
  slot table).

The entry point [`create_page`][pythonnative.create_page] is called
internally by the bundled native templates to bootstrap your root
component. App code does not call it directly.

## Styling

- **`style` prop**: pass a dict (or a list of dicts) to any
  component. For example, `style={"font_size": 24, "color": "#333"}`.
- **StyleSheet**: create reusable named style dictionaries with
  [`StyleSheet.create`][pythonnative.style.StyleSheet.create] and
  compose them with
  [`StyleSheet.compose`][pythonnative.style.StyleSheet.compose].
- **Theming**: use [`ThemeContext`][pythonnative.style.ThemeContext]
  with [`Provider`][pythonnative.Provider] and
  [`use_context`][pythonnative.use_context] to propagate theme
  values through the tree.

## Layout

PythonNative uses a **flexbox-inspired layout model** built on
platform-native layout managers.

[`View`][pythonnative.View] is the **universal flex container** (like
React Native's `View`). It defaults to `flex_direction: "column"`.
[`Column`][pythonnative.Column] and [`Row`][pythonnative.Row] are
convenience wrappers that fix the direction.

### Flex container properties (inside `style`)

- `flex_direction`: `"column"` (default), `"row"`, `"column_reverse"`,
  `"row_reverse"`.
- `justify_content`: main-axis distribution: `"flex_start"`,
  `"center"`, `"flex_end"`, `"space_between"`, `"space_around"`,
  `"space_evenly"`.
- `align_items`: cross-axis alignment: `"stretch"`, `"flex_start"`,
  `"center"`, `"flex_end"`.
- `overflow`: `"visible"` (default), `"hidden"`.
- `spacing`: gap between children (dp / pt).
- `padding`: inner spacing.

### Child layout properties

- `flex`: flex grow factor (shorthand).
- `flex_grow`, `flex_shrink`: individual flex properties.
- `align_self`: override the parent's `align_items` for this child.
- `width`, `height`: fixed dimensions.
- `min_width`, `min_height`: minimum size constraints.
- `margin`: outer spacing.

Under the hood:

- **Android**: `LinearLayout` with gravity, weights, and
  divider-based spacing.
- **iOS**: `UIStackView` with axis, alignment, distribution, and
  layout margins.

## Native view handlers

Platform-specific rendering logic lives in the
`pythonnative.native_views` package, organized into dedicated
submodules:

- `native_views.base`: shared
  [`ViewHandler`][pythonnative.native_views.base.ViewHandler] protocol
  and common utilities (color parsing, padding resolution, layout
  keys, flex constants).
- `native_views.android`: Android handlers using Chaquopy's Java
  bridge (`jclass`, `dynamic_proxy`).
- `native_views.ios`: iOS handlers using rubicon-objc
  (`ObjCClass`, `objc_method`).

`Column`, `Row`, and `View` share a single flex-container handler on
each platform. The handler reads `flex_direction` from the element's
props to configure the native layout container.

Each handler class maps an element type name (e.g., `"Text"`,
`"Button"`) to platform-native widget creation, property updates, and
child management. The
[`NativeViewRegistry`][pythonnative.native_views.NativeViewRegistry]
lazily imports only the relevant platform module at runtime, so the
package can be imported on any platform for testing.

## Comparisons

!!! note "Versus React Native"
    React Native uses JSX plus a JavaScript bridge (or JSI in newer
    versions) plus Yoga layout. PythonNative uses Python plus direct
    native calls plus platform layout managers; no JS bridge, no
    serialization overhead.

!!! note "Versus NativeScript"
    NativeScript shares the philosophy of direct, synchronous native
    access, but PythonNative adds a declarative reconciler layer and
    React-like hooks that NativeScript does not have by default.

See [Mental model](mental-model.md) for a wider comparison table.

## iOS flow (rubicon-objc)

- The iOS template (Swift plus PythonKit) boots Python and calls
  [`create_page`][pythonnative.create_page] internally with the
  current `UIViewController` pointer.
- The reconciler creates UIKit views and attaches them to the
  controller's view.
- State changes trigger re-renders; the reconciler patches UIKit
  views in place.

## Android flow (Chaquopy)

- The Android template (Kotlin plus Chaquopy) initializes Python in
  `MainActivity` and passes the `Activity` to Python.
- `PageFragment` calls [`create_page`][pythonnative.create_page]
  internally, which renders the root component and attaches views to
  the fragment container.
- State changes trigger re-render; the reconciler patches Android
  views in place.

## Hot reload

During development, `pn run --hot-reload` watches `app/` for file
changes and pushes updated Python files to the running app, enabling
near-instant UI updates without full rebuilds. See
[Hot reload guide](../guides/hot-reload.md).

## Native API modules

PythonNative provides cross-platform modules for common device APIs:

- [`Camera`][pythonnative.native_modules.camera.Camera]: photo
  capture and gallery picker.
- [`Location`][pythonnative.native_modules.location.Location]: GPS
  and location services.
- [`FileSystem`][pythonnative.native_modules.file_system.FileSystem]:
  app-scoped file I/O.
- [`Notifications`][pythonnative.native_modules.notifications.Notifications]:
  local notifications.

See [Native modules guide](../guides/native-modules.md).

## Navigation

PythonNative provides two navigation approaches:

- **Declarative navigators** (recommended):
  [`NavigationContainer`][pythonnative.NavigationContainer] with
  [`create_stack_navigator`][pythonnative.create_stack_navigator],
  [`create_tab_navigator`][pythonnative.create_tab_navigator], and
  [`create_drawer_navigator`][pythonnative.create_drawer_navigator].
  Navigation state is managed in Python as component state, and
  navigators are composable; you can nest tabs inside stacks, and so
  on.
- **Page-level navigation**:
  [`use_navigation`][pythonnative.use_navigation] returns a
  navigation handle with `.navigate()`, `.go_back()`, and
  `.get_params()`, delegating to native platform navigation when
  running on device.

Both approaches are supported. The declarative system uses the
existing reconciler pipeline; navigators are function components that
render the active screen via `use_state`, and navigation context is
provided via [`Provider`][pythonnative.Provider].

See the [Navigation guide](../guides/navigation.md) for full details.

- iOS: one host `UIViewController` class, many instances pushed on a
  `UINavigationController`.
- Android: single host `Activity` with a `NavHostFragment` and a
  stack of generic `PageFragment`s driven by a navigation graph.

## Next steps

- Read the [Mental model](mental-model.md) for the high-level
  comparisons.
- Walk through the render loop in [Lifecycle](lifecycle.md).
- See the platform handlers up close in [Native views](native-views.md).
- Browse the API: [Package overview](../api/pythonnative.md).
