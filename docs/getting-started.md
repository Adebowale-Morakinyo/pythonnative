# Getting Started

```bash
pip install pythonnative
pn --help
```

## Create a project

```bash
pn init MyApp
```

This scaffolds:

- `app/` with a minimal `main_page.py`
- `pythonnative.json` project config
- `requirements.txt`
- `.gitignore`

A minimal `app/main_page.py` looks like:

```python
import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def on_create(self):
        super().on_create()
        stack = pn.StackView()
        stack.add_view(pn.Label("Hello from PythonNative!"))
        button = pn.Button("Tap me")
        button.set_on_click(lambda: print("Button clicked"))
        stack.add_view(button)
        self.set_root_view(stack)


def bootstrap(native_instance):
    """Entry point called by the host app (Activity or ViewController)."""
    page = MainPage(native_instance)
    page.on_create()
    return page
```

## Run on a platform

```bash
pn run android
# or
pn run ios
```

- Uses bundled templates (no network required for scaffolding)
- Copies your `app/` into the generated project

If you just want to scaffold the platform project without building, use:

```bash
pn run android --prepare-only
pn run ios --prepare-only
```

This stages files under `build/` so you can open them in Android Studio or Xcode.

## Clean

Remove the build artifacts safely:

```bash
pn clean
```
