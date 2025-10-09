# pythonnative package

API reference will be generated here via mkdocstrings.

Key flags and helpers (0.2.0):

- `pythonnative.utils.IS_ANDROID`: platform flag with robust detection for Chaquopy/Android.
- `pythonnative.utils.get_android_context()`: returns the current Android Activity/Context when running on Android.
- `pythonnative.utils.set_android_context(ctx)`: set by `pythonnative.Page` on Android; you generally don’t call this directly.
