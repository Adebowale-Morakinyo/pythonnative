# pythonnative package

## Public API

### create_page

`pythonnative.create_page(...)` — called internally by native templates to bootstrap the root component. You don't call this directly.

### Element functions

- `pythonnative.Text`, `Button`, `Column`, `Row`, `ScrollView`, `TextInput`, `Image`, `Switch`, `ProgressBar`, `ActivityIndicator`, `WebView`, `Spacer`
- `pythonnative.View`, `SafeAreaView`, `Modal`, `Slider`, `Pressable`, `FlatList`

Each returns an `Element` descriptor. Visual and layout properties are passed via `style={...}`. See the Component Property Reference for full details.

### ErrorBoundary

`pythonnative.ErrorBoundary(child, fallback=...)` — catches render errors in *child* and displays *fallback* instead. *fallback* may be an `Element` or a callable that receives the exception and returns an `Element`.

### Element

`pythonnative.Element` — the descriptor type returned by element functions. You generally don't create these directly.

### Hooks

Function component primitives:

- `pythonnative.component` — decorator to create a function component
- `pythonnative.use_state(initial)` — local component state
- `pythonnative.use_reducer(reducer, initial_state)` — reducer-based state management; returns `(state, dispatch)`
- `pythonnative.use_effect(effect, deps)` — side effects, run after native commit
- `pythonnative.use_navigation()` — navigation handle (navigate/go_back/get_params)
- `pythonnative.use_route()` — convenience hook for current route params
- `pythonnative.use_focus_effect(effect, deps)` — like `use_effect` but only runs when the screen is focused
- `pythonnative.use_memo(factory, deps)` — memoised values
- `pythonnative.use_callback(fn, deps)` — stable function references
- `pythonnative.use_ref(initial)` — mutable ref object
- `pythonnative.use_context(context)` — read from context
- `pythonnative.create_context(default)` — create a new context
- `pythonnative.Provider(context, value, child)` — provide a context value

### Navigation

Declarative, component-based navigation system:

- `pythonnative.NavigationContainer(child)` — root container for the navigation tree
- `pythonnative.create_stack_navigator()` — create a stack-based navigator (returns object with `.Navigator` and `.Screen`)
- `pythonnative.create_tab_navigator()` — create a tab-based navigator
- `pythonnative.create_drawer_navigator()` — create a drawer-based navigator

### Batching

- `pythonnative.batch_updates()` — context manager that batches multiple state updates into a single re-render

### Styling

- `pythonnative.StyleSheet` — utility for creating and composing style dicts
- `pythonnative.ThemeContext` — built-in theme context (defaults to light theme)

## Native API modules

- `pythonnative.native_modules.Camera` — photo capture and gallery picking
- `pythonnative.native_modules.Location` — GPS / location services
- `pythonnative.native_modules.FileSystem` — app-scoped file I/O
- `pythonnative.native_modules.Notifications` — local push notifications

## Internal helpers

- `pythonnative.utils.IS_ANDROID` — platform flag with robust detection for Chaquopy/Android.
- `pythonnative.utils.get_android_context()` — returns the current Android `Activity`/`Context` when running on Android.
- `pythonnative.utils.set_android_context(ctx)` — set internally during page bootstrapping; you generally don't call this directly.
- `pythonnative.utils.get_android_fragment_container()` — returns the current Fragment container `ViewGroup` used for page rendering.

## Reconciler

`pythonnative.reconciler.Reconciler` — diffs element trees and applies minimal native mutations. Supports key-based child reconciliation, function components, context providers, and error boundaries. Effects are flushed after each mount/reconcile pass. Used internally by `create_page`.

## Hot reload

`pythonnative.hot_reload.FileWatcher` — watches a directory for file changes and triggers a callback. Used by `pn run --hot-reload`.

`pythonnative.hot_reload.ModuleReloader` — reloads changed Python modules on the device and triggers page re-rendering.

## Native view registry

`pythonnative.native_views.NativeViewRegistry` — maps element type names to platform-specific handlers. Use `set_registry()` to inject a mock for testing.

The `native_views` package is organised into submodules:

- `pythonnative.native_views.base` — shared `ViewHandler` protocol and utilities (`parse_color_int`, `resolve_padding`, `LAYOUT_KEYS`)
- `pythonnative.native_views.android` — Android handlers (only imported at runtime on Android via Chaquopy)
- `pythonnative.native_views.ios` — iOS handlers (only imported at runtime on iOS via rubicon-objc)
