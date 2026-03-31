# pythonnative package

## Public API

### Page

`pythonnative.Page` — base class for screens. Subclass it, implement `render()`, and use `set_state()` to trigger re-renders.

### Element functions

- `pythonnative.Text`, `Button`, `Column`, `Row`, `ScrollView`, `TextInput`, `Image`, `Switch`, `ProgressBar`, `ActivityIndicator`, `WebView`, `Spacer`

Each returns an `Element` descriptor. See the Component Property Reference for full signatures.

### Element

`pythonnative.Element` — the descriptor type returned by element functions. You generally don't create these directly.

## Internal helpers

- `pythonnative.utils.IS_ANDROID` — platform flag with robust detection for Chaquopy/Android.
- `pythonnative.utils.get_android_context()` — returns the current Android `Activity`/`Context` when running on Android.
- `pythonnative.utils.set_android_context(ctx)` — set by `Page` on Android; you generally don't call this directly.
- `pythonnative.utils.get_android_fragment_container()` — returns the current Fragment container `ViewGroup` used for page rendering.
- `pythonnative.utils.set_android_fragment_container(viewGroup)` — set by the host `PageFragment`; you generally don't call this directly.

## Reconciler

`pythonnative.reconciler.Reconciler` — diffs element trees and applies minimal native mutations. Used internally by `Page`.

## Native view registry

`pythonnative.native_views.NativeViewRegistry` — maps element type names to platform-specific handlers. Use `set_registry()` to inject a mock for testing.
