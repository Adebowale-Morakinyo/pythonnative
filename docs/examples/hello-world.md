# Hello World

Create a simple component with a counter that increments on tap.

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

Run it:

```bash
pn run android
# or
pn run ios
```
