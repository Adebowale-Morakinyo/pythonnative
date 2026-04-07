# Components

PythonNative uses a **declarative component model** inspired by React. You describe *what* the UI should look like, and the framework handles creating and updating native views.

## Element functions

UI is built with element-creating functions. Each returns a lightweight `Element` descriptor — no native objects are created until the reconciler mounts the tree.

```python
import pythonnative as pn

pn.Text("Hello", style={"font_size": 18, "color": "#333333"})
pn.Button("Tap me", on_click=lambda: print("tapped"))
pn.Column(
    pn.Text("First"),
    pn.Text("Second"),
    style={"spacing": 8, "padding": 16},
)
```

### Available components

**Layout:**

- `View(*children, style=...)` — universal flex container (default `flex_direction: "column"`)
- `Column(*children, style=...)` — vertical flex container (fixed `flex_direction: "column"`)
- `Row(*children, style=...)` — horizontal flex container (fixed `flex_direction: "row"`)
- `ScrollView(child, style=...)` — scrollable container
- `SafeAreaView(*children, style=...)` — safe-area-aware container
- `Spacer(size, flex)` — empty space

**Display:**

- `Text(text, style=...)` — text display
- `Image(source, style=...)` — image display (supports URLs and resource names)
- `WebView(url)` — embedded web content

**Input:**

- `Button(title, on_click, style=...)` — tappable button
- `TextInput(value, placeholder, on_change, secure, style=...)` — text entry
- `Switch(value, on_change)` — toggle switch
- `Slider(value, min_value, max_value, on_change)` — continuous slider
- `Pressable(child, on_press, on_long_press)` — tap handler wrapper

**Feedback:**

- `ProgressBar(value)` — determinate progress (0.0–1.0)
- `ActivityIndicator(animating)` — indeterminate spinner

**Overlay:**

- `Modal(*children, visible, on_dismiss, title)` — modal dialog

**Error handling:**

- `ErrorBoundary(child, fallback)` — catches render errors in child and displays fallback

**Lists:**

- `FlatList(data, render_item, key_extractor, separator_height)` — scrollable data list

### Flex layout model

PythonNative uses a **flexbox-inspired layout model**. `View` is the universal flex container — `Column` and `Row` are convenience wrappers.

#### Flex container properties (inside `style`)

- `flex_direction` — `"column"` (default), `"row"`, `"column_reverse"`, `"row_reverse"`
- `justify_content` — main-axis distribution: `"flex_start"`, `"center"`, `"flex_end"`, `"space_between"`, `"space_around"`, `"space_evenly"`
- `align_items` — cross-axis alignment: `"stretch"`, `"flex_start"`, `"center"`, `"flex_end"`
- `overflow` — `"visible"` (default), `"hidden"`
- `spacing` — gap between children (dp / pt)
- `padding` — inner spacing

#### Child layout properties

All components accept these in their `style` dict:

- `width`, `height` — fixed dimensions (dp / pt)
- `flex` — flex grow factor (shorthand)
- `flex_grow`, `flex_shrink` — individual flex properties
- `margin` — outer margin (int, float, or dict like padding)
- `min_width`, `min_height` — minimum size constraints
- `max_width`, `max_height` — maximum size constraints
- `align_self` — override parent alignment for this child

#### Example: centering content

```python
pn.View(
    pn.Text("Centered"),
    style={"flex": 1, "justify_content": "center", "align_items": "center"},
)
```

#### Example: horizontal row with spacing

```python
pn.Row(
    pn.Button("Cancel"),
    pn.Spacer(flex=1),
    pn.Button("OK"),
    style={"padding": 16, "align_items": "center"},
)
```

## Function components — the building block

All UI in PythonNative is built with `@pn.component` function components. Each screen is a function component that returns an element tree:

```python
@pn.component
def MainPage():
    name, set_name = pn.use_state("World")
    return pn.Text(f"Hello, {name}!", style={"font_size": 24})
```

The entry point `create_page()` is called internally by native templates to bootstrap your root component. You don't call it directly — just export your component and configure the entry point in `pythonnative.json`.

## State and re-rendering

Use `pn.use_state(initial)` to create local component state. Call the setter to update — the framework automatically re-renders the component and applies only the differences to the native views:

```python
@pn.component
def CounterPage():
    count, set_count = pn.use_state(0)

    return pn.Column(
        pn.Text(f"Count: {count}", style={"font_size": 24}),
        pn.Button("Increment", on_click=lambda: set_count(count + 1)),
        style={"spacing": 12},
    )
```

## Composing components

Build complex UIs by composing smaller `@pn.component` functions. Each instance has **independent state**:

```python
@pn.component
def Counter(label: str = "Count", initial: int = 0):
    count, set_count = pn.use_state(initial)

    return pn.Column(
        pn.Text(f"{label}: {count}", style={"font_size": 18}),
        pn.Row(
            pn.Button("-", on_click=lambda: set_count(count - 1)),
            pn.Button("+", on_click=lambda: set_count(count + 1)),
            style={"spacing": 8},
        ),
        style={"spacing": 4},
    )


@pn.component
def MainPage():
    return pn.Column(
        Counter(label="Apples", initial=0),
        Counter(label="Oranges", initial=5),
        style={"spacing": 16, "padding": 16},
    )
```

Changing one `Counter` doesn't affect the other — each has its own hook state.

### Available hooks

- `use_state(initial)` — local component state; returns `(value, setter)`
- `use_reducer(reducer, initial_state)` — reducer-based state; returns `(state, dispatch)`
- `use_effect(effect, deps)` — side effects, run after native commit (timers, API calls, subscriptions)
- `use_memo(factory, deps)` — memoised computed values
- `use_callback(fn, deps)` — stable function references
- `use_ref(initial)` — mutable ref that persists across renders
- `use_context(context)` — read from a context provider
- `use_navigation()` — navigation handle for navigate/go_back/get_params
- `use_route()` — convenience hook for current route params
- `use_focus_effect(effect, deps)` — like `use_effect` but only runs when the screen is focused

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

@pn.component
def App():
    return pn.Provider(theme, {"primary": "#FF0000"},
        MyComponent()
    )

@pn.component
def MyComponent():
    t = pn.use_context(theme)
    return pn.Button("Click", style={"color": t["primary"]})
```

## Platform detection

Use `pythonnative.utils.IS_ANDROID` when you need platform-specific logic:

```python
from pythonnative.utils import IS_ANDROID

title = "Android App" if IS_ANDROID else "iOS App"
```
