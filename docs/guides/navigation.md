# Navigation

This guide shows how to navigate between pages and handle lifecycle events.

## Push / Pop

Use `push` and `pop` on your `Page` to change screens. You can pass a dotted path string or a class reference.

```python
import pythonnative as pn

class MainPage(pn.Page):
    def on_create(self):
        stack = pn.StackView()
        btn = pn.Button("Go next")
        btn.set_on_click(lambda: self.push("app.second_page.SecondPage", args={"message": "Hello"}))
        stack.add_view(btn)
        self.set_root_view(stack)
```

On the target page:

```python
class SecondPage(pn.Page):
    def on_create(self):
        args = self.get_args()
        message = args.get("message", "Second")
        stack = pn.StackView()
        stack.add_view(pn.Label(message))
        back = pn.Button("Back")
        back.set_on_click(lambda: self.pop())
        stack.add_view(back)
        self.set_root_view(stack)
```

## Lifecycle

PythonNative forwards lifecycle events from the host:

- `on_create`
- `on_start`
- `on_resume`
- `on_pause`
- `on_stop`
- `on_destroy`
- `on_restart` (Android only)
- `on_save_instance_state`
- `on_restore_instance_state`

Android forwards Activity lifecycle via the template `MainActivity` and `PageActivity`. iOS forwards `viewWillAppear`/`viewWillDisappear` via an internal registry.

## Notes

- On Android, `push` launches a template `PageActivity` and passes `PY_PAGE_PATH` and optional JSON args.
- On iOS, `push` uses the root `UINavigationController` to push a new `ViewController` and passes page info via KVC.
