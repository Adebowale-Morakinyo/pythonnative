# Examples

A collection of examples showing PythonNative's declarative component model and patterns.

## Quick counter

```python
import pythonnative as pn


class CounterPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)
        self.state = {"count": 0}

    def render(self):
        return pn.Column(
            pn.Text(f"Count: {self.state['count']}", font_size=24),
            pn.Button(
                "Increment",
                on_click=lambda: self.set_state(count=self.state["count"] + 1),
            ),
            spacing=12,
            padding=16,
        )
```

## Reusable components

```python
def labeled_input(label, placeholder=""):
    return pn.Column(
        pn.Text(label, font_size=14, bold=True),
        pn.TextInput(placeholder=placeholder),
        spacing=4,
    )


class FormPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def render(self):
        return pn.ScrollView(
            pn.Column(
                pn.Text("Sign Up", font_size=24, bold=True),
                labeled_input("Name", "Enter your name"),
                labeled_input("Email", "you@example.com"),
                pn.Button("Submit", on_click=lambda: print("submitted")),
                spacing=12,
                padding=16,
            )
        )
```

See `examples/hello-world/` for a full multi-page demo with navigation.
