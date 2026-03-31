# PythonNative

Build native Android and iOS apps with Python using a declarative, React-like component model.

PythonNative provides a Pythonic API for native UI components, a virtual view tree with automatic reconciliation, and a simple CLI to scaffold and run projects.

```python
import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)
        self.state = {"count": 0}

    def render(self):
        return pn.Column(
            pn.Text(f"Count: {self.state['count']}", font_size=24),
            pn.Button("Increment", on_click=lambda: self.set_state(count=self.state["count"] + 1)),
            spacing=12,
            padding=16,
        )
```
