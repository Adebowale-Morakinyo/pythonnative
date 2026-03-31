# Components

PythonNative uses a **declarative component model** inspired by React. You describe *what* the UI should look like, and the framework handles creating and updating native views.

## Element functions

UI is built with element-creating functions. Each returns a lightweight `Element` descriptor — no native objects are created until the reconciler mounts the tree.

```python
import pythonnative as pn

pn.Text("Hello", font_size=18, color="#333333")
pn.Button("Tap me", on_click=lambda: print("tapped"))
pn.Column(
    pn.Text("First"),
    pn.Text("Second"),
    spacing=8,
    padding=16,
)
```

### Available components

**Layout:**

- `Column(*children, spacing, padding, alignment, background_color)` — vertical stack
- `Row(*children, spacing, padding, alignment, background_color)` — horizontal stack
- `ScrollView(child, background_color)` — scrollable container
- `Spacer(size)` — empty space

**Display:**

- `Text(text, font_size, color, bold, text_align, background_color, max_lines)` — text display
- `Image(source, width, height, scale_type)` — image display
- `WebView(url)` — embedded web content

**Input:**

- `Button(title, on_click, color, background_color, font_size, enabled)` — tappable button
- `TextInput(value, placeholder, on_change, secure, font_size, color)` — text entry
- `Switch(value, on_change)` — toggle switch

**Feedback:**

- `ProgressBar(value)` — determinate progress (0.0–1.0)
- `ActivityIndicator(animating)` — indeterminate spinner

## Page — the root component

Each screen is a `Page` subclass with a `render()` method that returns an element tree:

```python
class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)
        self.state = {"name": "World"}

    def render(self):
        return pn.Text(f"Hello, {self.state['name']}!", font_size=24)
```

## State and re-rendering

Call `self.set_state(key=value)` to update state. The framework automatically calls `render()` again and applies only the differences to the native views:

```python
class CounterPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)
        self.state = {"count": 0}

    def increment(self):
        self.set_state(count=self.state["count"] + 1)

    def render(self):
        return pn.Column(
            pn.Text(f"Count: {self.state['count']}", font_size=24),
            pn.Button("Increment", on_click=self.increment),
            spacing=12,
        )
```

## Reusable components as functions

For reusable UI pieces, use regular Python functions that return elements:

```python
def greeting_card(name, on_tap):
    return pn.Column(
        pn.Text(f"Hello, {name}!", font_size=20, bold=True),
        pn.Button("Say hi", on_click=on_tap),
        spacing=8,
        padding=12,
    )

class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def render(self):
        return pn.Column(
            greeting_card("Alice", lambda: print("Hi Alice")),
            greeting_card("Bob", lambda: print("Hi Bob")),
            spacing=16,
        )
```

## Platform detection

Use `pythonnative.utils.IS_ANDROID` when you need platform-specific logic:

```python
from pythonnative.utils import IS_ANDROID

title = "Android App" if IS_ANDROID else "iOS App"
```

On Android, `Page` records the current `Activity` so component constructors can acquire a `Context` implicitly. Constructing views before `Page` initialisation will raise.
