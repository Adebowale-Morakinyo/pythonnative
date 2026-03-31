# Hello World

Create a simple page with a counter that increments on tap.

```python
import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)
        self.state = {"count": 0}

    def render(self):
        return pn.Column(
            pn.Text(f"Count: {self.state['count']}", font_size=24),
            pn.Button(
                "Tap me",
                on_click=lambda: self.set_state(count=self.state["count"] + 1),
            ),
            spacing=12,
            padding=16,
        )
```

Run it:

```bash
pn run android
# or
pn run ios
```
