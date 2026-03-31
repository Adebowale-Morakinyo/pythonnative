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
        self.state = {"count": 0}

    def render(self):
        return pn.Column(
            pn.Text(f"Count: {self.state['count']}", font_size=24),
            pn.Button(
                "Tap me",
                on_click=lambda: self.set_state(count=self.state["count"] + 1),
            ),
            spacing=12,
            padding=16,
        )
```

Key ideas:

- **`render()`** returns an element tree describing the UI. PythonNative creates and updates native views automatically.
- **`self.state`** holds your page's data. Call **`self.set_state(key=value)`** to update it — the UI re-renders automatically.
- Element functions like `pn.Text(...)`, `pn.Button(...)`, `pn.Column(...)` create lightweight descriptions, not native objects.

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
