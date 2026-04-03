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


@pn.component
def App():
    count, set_count = pn.use_state(0)
    return pn.Column(
        pn.Text(f"Count: {count}", style={"font_size": 24}),
        pn.Button(
            "Tap me",
            on_click=lambda: set_count(count + 1),
        ),
        style={"spacing": 12, "padding": 16},
    )
```

Key ideas:

- **`@pn.component`** marks a function as a PythonNative component. The function returns an element tree describing the UI. PythonNative creates and updates native views automatically.
- **`pn.use_state(initial)`** creates local component state. Call the setter to update it — the UI re-renders automatically.
- **`style={...}`** passes visual and layout properties as a dict (or list of dicts) to any component.
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
