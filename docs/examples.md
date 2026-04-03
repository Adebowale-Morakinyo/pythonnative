# Examples

A collection of examples showing PythonNative's declarative component model and patterns.

## Quick counter

```python
import pythonnative as pn


@pn.component
def Counter():
    count, set_count = pn.use_state(0)
    return pn.Column(
        pn.Text(f"Count: {count}", style={"font_size": 24}),
        pn.Button(
            "Increment",
            on_click=lambda: set_count(count + 1),
        ),
        style={"spacing": 12, "padding": 16},
    )
```

## Reusable components

```python
import pythonnative as pn


@pn.component
def LabeledInput(label: str = "", placeholder: str = ""):
    return pn.Column(
        pn.Text(label, style={"font_size": 14, "bold": True}),
        pn.TextInput(placeholder=placeholder),
        style={"spacing": 4},
    )


@pn.component
def FormPage():
    return pn.ScrollView(
        pn.Column(
            pn.Text("Sign Up", style={"font_size": 24, "bold": True}),
            LabeledInput(label="Name", placeholder="Enter your name"),
            LabeledInput(label="Email", placeholder="you@example.com"),
            pn.Button("Submit", on_click=lambda: print("submitted")),
            style={"spacing": 12, "padding": 16},
        )
    )
```

See `examples/hello-world/` for a full multi-page demo with navigation.
