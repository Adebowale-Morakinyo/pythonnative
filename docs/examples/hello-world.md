# Hello World

Create a simple page with a label and a button.

```python
import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def on_create(self):
        super().on_create()
        stack = pn.StackView()
        label = pn.Label("Hello, world!")
        button = pn.Button("Tap me")
        button.set_on_click(lambda: print("Hello tapped"))
        stack.add_view(label)
        stack.add_view(button)
        self.set_root_view(stack)
```

Run it:

```bash
pn run android
# or
pn run ios
```
