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
- `View(*children, background_color, padding)` — generic container
- `SafeAreaView(*children, background_color, padding)` — safe-area-aware container
- `Spacer(size, flex)` — empty space

**Display:**

- `Text(text, font_size, color, bold, text_align, background_color, max_lines)` — text display
- `Image(source, width, height, scale_type)` — image display (supports URLs and resource names)
- `WebView(url)` — embedded web content

**Input:**

- `Button(title, on_click, color, background_color, font_size, enabled)` — tappable button
- `TextInput(value, placeholder, on_change, secure, font_size, color)` — text entry
- `Switch(value, on_change)` — toggle switch
- `Slider(value, min_value, max_value, on_change)` — continuous slider
- `Pressable(child, on_press, on_long_press)` — tap handler wrapper

**Feedback:**

- `ProgressBar(value)` — determinate progress (0.0–1.0)
- `ActivityIndicator(animating)` — indeterminate spinner

**Overlay:**

- `Modal(*children, visible, on_dismiss, title)` — modal dialog

**Lists:**

- `FlatList(data, render_item, key_extractor, separator_height)` — scrollable data list

### Layout properties

All components support common layout properties:

- `width`, `height` — fixed dimensions (dp / pt)
- `flex` — flex grow factor
- `margin` — outer margin (int, float, or dict like padding)
- `min_width`, `max_width`, `min_height`, `max_height` — size constraints
- `align_self` — override parent alignment for this child

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

## Function components with hooks

For reusable UI pieces **with their own state**, use the `@pn.component` decorator and hooks:

```python
@pn.component
def counter(label: str = "Count", initial: int = 0) -> pn.Element:
    count, set_count = pn.use_state(initial)

    return pn.Column(
        pn.Text(f"{label}: {count}", font_size=18),
        pn.Row(
            pn.Button("-", on_click=lambda: set_count(count - 1)),
            pn.Button("+", on_click=lambda: set_count(count + 1)),
            spacing=8,
        ),
        spacing=4,
    )

class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def render(self):
        return pn.Column(
            counter(label="Apples", initial=0),
            counter(label="Oranges", initial=5),
            spacing=16,
            padding=16,
        )
```

Each `counter` instance has **independent state** — changing one doesn't affect the other.

### Available hooks

- `use_state(initial)` — local component state; returns `(value, setter)`
- `use_effect(effect, deps)` — side effects (timers, API calls, subscriptions)
- `use_memo(factory, deps)` — memoised computed values
- `use_callback(fn, deps)` — stable function references
- `use_ref(initial)` — mutable ref that persists across renders
- `use_context(context)` — read from a context provider

### Custom hooks

Extract reusable stateful logic into plain functions:

```python
def use_toggle(initial: bool = False):
    value, set_value = pn.use_state(initial)
    def toggle():
        set_value(not value)
    return value, toggle
```

### Context and Provider

Share values across the tree without prop drilling:

```python
theme = pn.create_context({"primary": "#007AFF"})

# In a page's render():
pn.Provider(theme, {"primary": "#FF0000"},
    my_component()
)

# In my_component:
@pn.component
def my_component() -> pn.Element:
    t = pn.use_context(theme)
    return pn.Button("Click", color=t["primary"])
```

## Platform detection

Use `pythonnative.utils.IS_ANDROID` when you need platform-specific logic:

```python
from pythonnative.utils import IS_ANDROID

title = "Android App" if IS_ANDROID else "iOS App"
```

On Android, `Page` records the current `Activity` so component constructors can acquire a `Context` implicitly. Constructing views before `Page` initialisation will raise.
