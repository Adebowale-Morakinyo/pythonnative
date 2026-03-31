# Architecture

PythonNative combines **direct native bindings** with a **declarative reconciler**, giving you React-like ergonomics while calling native platform APIs synchronously from Python.

## High-level model

1. **Declarative element tree:** Your `Page.render()` method returns a tree of `Element` descriptors (similar to React elements / virtual DOM nodes).
2. **Reconciler:** On first render, the reconciler walks the tree and creates real native views via the platform backend. On subsequent renders (triggered by `set_state`), it diffs the new tree against the old one and applies the minimal set of native mutations.
3. **Direct bindings:** Under the hood, native views are created and updated through direct platform calls:
   - **iOS:** rubicon-objc exposes Objective-C/Swift classes (`UILabel`, `UIButton`, `UIStackView`, etc.).
   - **Android:** Chaquopy exposes Java classes (`android.widget.TextView`, `android.widget.Button`, etc.) via the JNI bridge.
4. **Thin native bootstrap:** The host app remains native (Android `Activity` or iOS `UIViewController`). It passes a live instance/pointer into Python, and Python drives the UI through the reconciler.

## How it works

```
Page.render()  →  Element tree  →  Reconciler  →  Native views
                                       ↑
Page.set_state()  →  re-render  →  diff  →  patch native views
```

The reconciler uses **positional diffing** (comparing children by index). When a child at a given position has the same element type, its props are updated in-place on the native view. When the type changes, the old native view is destroyed and a new one is created.

## Comparison

- **Versus React Native:** RN uses JSX + a JavaScript bridge + Yoga layout. PythonNative uses Python + direct native calls + platform layout managers. No JS bridge, no serialisation overhead.
- **Versus NativeScript:** Similar philosophy (direct, synchronous native access), but PythonNative adds a declarative reconciler layer that NativeScript does not have by default.
- **Versus the old imperative API:** The previous PythonNative API required manual `add_view()` calls and explicit setter methods. The new declarative model handles view lifecycle automatically.

## iOS flow (Rubicon-ObjC)

- The iOS template (Swift + PythonKit) boots Python and instantiates your `MainPage` with the current `UIViewController` pointer.
- `Page.on_create()` calls `render()`, the reconciler creates UIKit views, and attaches them to the controller's view.
- State changes trigger `render()` again; the reconciler patches UIKit views in-place.

## Android flow (Chaquopy)

- The Android template (Kotlin + Chaquopy) initializes Python in `MainActivity` and passes the `Activity` to Python.
- `PageFragment` calls `on_create()` on the Python `Page`, which renders and attaches views to the fragment container.
- State changes trigger re-render; the reconciler patches Android views in-place.

## Navigation model overview

- See the Navigation guide for full details.
  - iOS: one host `UIViewController` class, many instances pushed on a `UINavigationController`.
  - Android: single host `Activity` with a `NavHostFragment` and a stack of generic `PageFragment`s driven by a navigation graph.

## Related docs

- Guides / Android: guides/android.md
- Guides / iOS: guides/ios.md
- Concepts / Components: concepts/components.md
