# Function Components and Hooks

PythonNative supports React-like function components with hooks for managing state, effects, memoisation, and context. This is the recommended way to build reusable UI pieces.

## Creating a function component

Decorate a Python function with `@pn.component`:

```python
import pythonnative as pn

@pn.component
def greeting(name: str = "World") -> pn.Element:
    return pn.Text(f"Hello, {name}!", font_size=20)
```

Use it like any other component:

```python
class MyPage(pn.Page):
    def render(self):
        return pn.Column(
            greeting(name="Alice"),
            greeting(name="Bob"),
            spacing=12,
        )
```

## Hooks

Hooks let function components manage state and side effects. They must be called at the top level of a `@pn.component` function (not inside loops or conditions).

### use_state

Local component state. Returns `(value, setter)`.

```python
@pn.component
def counter(initial: int = 0) -> pn.Element:
    count, set_count = pn.use_state(initial)

    return pn.Column(
        pn.Text(f"Count: {count}"),
        pn.Button("+", on_click=lambda: set_count(count + 1)),
    )
```

The setter accepts a value or a function that receives the current value:

```python
set_count(10)                     # set directly
set_count(lambda prev: prev + 1) # functional update
```

If the initial value is expensive to compute, pass a callable:

```python
count, set_count = pn.use_state(lambda: compute_default())
```

### use_effect

Run side effects after render. The effect function may return a cleanup callable.

```python
@pn.component
def timer() -> pn.Element:
    seconds, set_seconds = pn.use_state(0)

    def tick():
        import threading
        t = threading.Timer(1.0, lambda: set_seconds(seconds + 1))
        t.start()
        return t.cancel  # cleanup: cancel the timer

    pn.use_effect(tick, [seconds])

    return pn.Text(f"Elapsed: {seconds}s")
```

Dependency control:

- `pn.use_effect(fn, None)` — run on every render
- `pn.use_effect(fn, [])` — run on mount only
- `pn.use_effect(fn, [a, b])` — run when `a` or `b` change

### use_memo

Memoise an expensive computation:

```python
sorted_items = pn.use_memo(lambda: sorted(items, key=lambda x: x.name), [items])
```

### use_callback

Return a stable function reference (avoids unnecessary re-renders of children):

```python
handle_click = pn.use_callback(lambda: set_count(count + 1), [count])
```

### use_ref

A mutable container that persists across renders without triggering re-renders:

```python
render_count = pn.use_ref(0)
render_count["current"] += 1
```

### use_context

Read a value from the nearest `Provider` ancestor:

```python
theme = pn.use_context(pn.ThemeContext)
color = theme["primary_color"]
```

## Context and Provider

Share values through the component tree without passing props manually:

```python
# Create a context with a default value
user_context = pn.create_context({"name": "Guest"})

# Provide a value to descendants
pn.Provider(user_context, {"name": "Alice"},
    user_profile()
)

# Consume in any descendant
@pn.component
def user_profile() -> pn.Element:
    user = pn.use_context(user_context)
    return pn.Text(f"Welcome, {user['name']}")
```

## Custom hooks

Extract reusable stateful logic into plain functions:

```python
def use_toggle(initial: bool = False):
    value, set_value = pn.use_state(initial)
    toggle = pn.use_callback(lambda: set_value(not value), [value])
    return value, toggle

def use_text_input(initial: str = ""):
    text, set_text = pn.use_state(initial)
    return text, set_text
```

Use them in any component:

```python
@pn.component
def settings() -> pn.Element:
    dark_mode, toggle_dark = use_toggle(False)

    return pn.Column(
        pn.Text("Settings", font_size=24, bold=True),
        pn.Row(
            pn.Text("Dark mode"),
            pn.Switch(value=dark_mode, on_change=lambda v: toggle_dark()),
        ),
    )
```

## Rules of hooks

1. Only call hooks inside `@pn.component` functions
2. Call hooks at the top level — not inside loops, conditions, or nested functions
3. Hooks must be called in the same order on every render
