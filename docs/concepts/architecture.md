# Architecture

PythonNative combines **direct native bindings** with a **declarative reconciler**, giving you React-like ergonomics while calling native platform APIs synchronously from Python.

## High-level model

1. **Declarative element tree:** Your `@pn.component` function returns a tree of `Element` descriptors (similar to React elements / virtual DOM nodes).
2. **Function components and hooks:** All UI is built with `@pn.component` functions using `use_state`, `use_effect`, `use_navigation`, etc. — inspired by React hooks but designed for Python.
3. **Reconciler:** On first render, the reconciler walks the tree and creates real native views via the platform backend. On subsequent renders (triggered by hook state changes), it diffs the new tree against the old one and applies the minimal set of native mutations.
4. **Key-based reconciliation:** Children can be assigned stable `key` values to preserve identity across re-renders — critical for lists and dynamic content.
5. **Direct bindings:** Under the hood, native views are created and updated through direct platform calls:
   - **iOS:** rubicon-objc exposes Objective-C/Swift classes (`UILabel`, `UIButton`, `UIStackView`, etc.).
   - **Android:** Chaquopy exposes Java classes (`android.widget.TextView`, `android.widget.Button`, etc.) via the JNI bridge.
6. **Thin native bootstrap:** The host app remains native (Android `Activity` or iOS `UIViewController`). It calls `create_page()` internally to bootstrap your Python component, and the reconciler drives the UI from there.

## How it works

```
@pn.component fn  →  Element tree  →  Reconciler  →  Native views
                                           ↑
Hook set_state()  →  re-render  →  diff  →  patch native views
```

The reconciler uses **key-based diffing** (matching children by key first, then by position). When a child with the same key/type is found, its props are updated in-place on the native view. When the type changes, the old native view is destroyed and a new one is created.

## Component model

PythonNative uses a single component model: **function components** decorated with `@pn.component`.

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
- Accepts props as keyword arguments
- Uses hooks for state (`use_state`), side effects (`use_effect`), navigation (`use_navigation`), and more
- Returns an `Element` tree describing the UI
- Each call site creates an independent instance with its own hook state

The entry point `create_page()` is called internally by native templates to bootstrap your root component. You don't call it directly.

## Styling

- **`style` prop:** Pass a dict (or list of dicts) to any component — `style={"font_size": 24, "color": "#333"}`.
- **StyleSheet:** Create reusable named style dictionaries with `pn.StyleSheet.create(...)`.
- **Theming:** Use `pn.ThemeContext` with `pn.Provider` and `pn.use_context` to propagate theme values through the tree.

## Layout

All components support layout properties inside the `style` dict: `width`, `height`, `flex`, `margin`, `min_width`, `max_width`, `min_height`, `max_height`, `align_self`. Containers (`Column`, `Row`) support `spacing`, `padding`, `alignment`, `align_items`, and `justify_content`.

## Comparison

- **Versus React Native:** RN uses JSX + a JavaScript bridge + Yoga layout. PythonNative uses Python + direct native calls + platform layout managers. No JS bridge, no serialisation overhead.
- **Versus NativeScript:** Similar philosophy (direct, synchronous native access), but PythonNative adds a declarative reconciler layer and React-like hooks that NativeScript does not have by default.

## iOS flow (Rubicon-ObjC)

- The iOS template (Swift + PythonKit) boots Python and calls `create_page()` internally with the current `UIViewController` pointer.
- The reconciler creates UIKit views and attaches them to the controller's view.
- State changes trigger re-renders; the reconciler patches UIKit views in-place.

## Android flow (Chaquopy)

- The Android template (Kotlin + Chaquopy) initializes Python in `MainActivity` and passes the `Activity` to Python.
- `PageFragment` calls `create_page()` internally, which renders the root component and attaches views to the fragment container.
- State changes trigger re-render; the reconciler patches Android views in-place.

## Hot reload

During development, `pn run --hot-reload` watches `app/` for file changes and pushes updated Python files to the running app, enabling near-instant UI updates without full rebuilds.

## Native API modules

PythonNative provides cross-platform modules for common device APIs:

- `pythonnative.native_modules.Camera` — photo capture and gallery
- `pythonnative.native_modules.Location` — GPS / location services
- `pythonnative.native_modules.FileSystem` — app-scoped file I/O
- `pythonnative.native_modules.Notifications` — local push notifications

## Navigation model overview

- See the Navigation guide for full details.
  - Navigation is handled via the `use_navigation()` hook, which returns a `NavigationHandle` with `.push()`, `.pop()`, and `.get_args()`.
  - iOS: one host `UIViewController` class, many instances pushed on a `UINavigationController`.
  - Android: single host `Activity` with a `NavHostFragment` and a stack of generic `PageFragment`s driven by a navigation graph.

## Related docs

- Guides / Android: guides/android.md
- Guides / iOS: guides/ios.md
- Concepts / Components: concepts/components.md
