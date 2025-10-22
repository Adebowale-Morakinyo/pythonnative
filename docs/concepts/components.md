# Components

High-level overview of PythonNative components and how they map to native UI.

## Constructor pattern

- All core components share a consistent, contextless constructor on both platforms.
- On Android, a `Context` is acquired implicitly from the current `Activity` set by `pn.Page`.
- On iOS, UIKit classes are allocated/initialized directly.

Examples:

```python
import pythonnative as pn

class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def on_create(self):
        super().on_create()
        stack = pn.StackView()
        stack.add_view(pn.Label("Hello"))
        stack.add_view(pn.Button("Tap me"))
        stack.add_view(pn.TextField("initial"))
        self.set_root_view(stack)
```

Notes:
- `pn.Page` stores the Android `Activity` so components like `pn.Button()` and `pn.Label()` can construct their native counterparts.
- If you construct views before the `Page` is created on Android, a runtime error will be raised because no `Context` is available.

## Core components

Stabilized with contextless constructors on both platforms:

- `Page`
- `StackView`
- `Label`, `Button`
- `ImageView`
- `TextField`, `TextView`
- `Switch`
- `ProgressView`, `ActivityIndicatorView`
- `WebView`

APIs are intentionally small and grow progressively in later releases. Properties and setters are kept consistent where supported by both platforms.

## Platform detection and Android context

- Use `pythonnative.utils.IS_ANDROID` for platform checks when needed.
- On Android, `Page` records the current `Activity` so child views can acquire a `Context` implicitly. Constructing views before `Page` initialization will raise.
