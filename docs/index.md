# PythonNative

Build native Android and iOS apps with Python using a declarative, React-like component model.

PythonNative provides a Pythonic API for native UI components, a virtual view tree with automatic reconciliation, and a simple CLI to scaffold and run projects.

```python
import pythonnative as pn


@pn.component
def App():
    count, set_count = pn.use_state(0)
    return pn.Column(
        pn.Text(f"Count: {count}", style={"font_size": 24}),
        pn.Button("Tap me", on_click=lambda: set_count(count + 1)),
        style={"spacing": 12, "padding": 16},
    )
```
