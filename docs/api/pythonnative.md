# pythonnative package

## Public API

### create_page

`pythonnative.create_page(...)` — called internally by native templates to bootstrap the root component. You don't call this directly.

### Element functions

- `pythonnative.Text`, `Button`, `Column`, `Row`, `ScrollView`, `TextInput`, `Image`, `Switch`, `ProgressBar`, `ActivityIndicator`, `WebView`, `Spacer`
- `pythonnative.View`, `SafeAreaView`, `Modal`, `Slider`, `Pressable`, `FlatList`

Each returns an `Element` descriptor. Visual and layout properties are passed via `style={...}`. See the Component Property Reference for full details.

### Element

`pythonnative.Element` — the descriptor type returned by element functions. You generally don't create these directly.

### Hooks

Function component primitives:

- `pythonnative.component` — decorator to create a function component
- `pythonnative.use_state(initial)` — local component state
- `pythonnative.use_effect(effect, deps)` — side effects
- `pythonnative.use_navigation()` — navigation handle (push/pop/get_args)
- `pythonnative.use_memo(factory, deps)` — memoised values
- `pythonnative.use_callback(fn, deps)` — stable function references
- `pythonnative.use_ref(initial)` — mutable ref object
- `pythonnative.use_context(context)` — read from context
- `pythonnative.create_context(default)` — create a new context
- `pythonnative.Provider(context, value, child)` — provide a context value

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

`pythonnative.reconciler.Reconciler` — diffs element trees and applies minimal native mutations. Supports key-based child reconciliation, function components, and context providers. Used internally by `create_page`.

## Hot reload

`pythonnative.hot_reload.FileWatcher` — watches a directory for file changes and triggers a callback. Used by `pn run --hot-reload`.

`pythonnative.hot_reload.ModuleReloader` — reloads changed Python modules on the device and triggers page re-rendering.

## Native view registry

`pythonnative.native_views.NativeViewRegistry` — maps element type names to platform-specific handlers. Use `set_registry()` to inject a mock for testing.
