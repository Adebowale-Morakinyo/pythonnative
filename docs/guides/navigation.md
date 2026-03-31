# Navigation

This guide shows how to navigate between pages and pass data.

## Push / Pop

Use `push` and `pop` on your `Page` to change screens. Pass a dotted path string or a class reference, with optional `args`.

```python
import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def render(self):
        return pn.Column(
            pn.Text("Main Page", font_size=24),
            pn.Button(
                "Go next",
                on_click=lambda: self.push(
                    "app.second_page.SecondPage",
                    args={"message": "Hello from Main"},
                ),
            ),
            spacing=12,
            padding=16,
        )
```

On the target page, retrieve args with `self.get_args()`:

```python
class SecondPage(pn.Page):
    def __init__(self, native_instance):
        super().__init__(native_instance)

    def render(self):
        message = self.get_args().get("message", "Second Page")
        return pn.Column(
            pn.Text(message, font_size=20),
            pn.Button("Back", on_click=self.pop),
            spacing=12,
            padding=16,
        )
```

## Lifecycle

PythonNative forwards lifecycle events from the host:

- `on_create` — triggers the initial `render()`
- `on_start`
- `on_resume`
- `on_pause`
- `on_stop`
- `on_destroy`
- `on_restart` (Android only)
- `on_save_instance_state`
- `on_restore_instance_state`

Override any of these on your `Page` subclass to respond to lifecycle changes.

## Notes

- On Android, `push` navigates via `NavController` to a `PageFragment` and passes `page_path` and optional JSON `args`.
- On iOS, `push` uses the root `UINavigationController` to push a new `ViewController` and passes page info via KVC.

## Platform specifics

### iOS (UIViewController per page)
- Each PythonNative page is hosted by a Swift `ViewController` instance.
- Pages are pushed and popped on a root `UINavigationController`.
- Lifecycle is forwarded from Swift to the registered Python page instance.

### Android (single Activity, Fragment stack)
- Single host `MainActivity` sets a `NavHostFragment` containing a navigation graph.
- Each PythonNative page is represented by a generic `PageFragment` which instantiates the Python page and attaches its root view.
- `push`/`pop` delegate to `NavController` (via a small `Navigator` helper).
- Arguments live in Fragment arguments and restore across configuration changes.

## Comparison to other frameworks
- **React Native:** Android: single `Activity`, screens managed via `Fragment`s. iOS: screens map to `UIViewController`s pushed on `UINavigationController`.
- **NativeScript:** Android: single `Activity`, pages as `Fragment`s. iOS: pages as `UIViewController`s on `UINavigationController`.
- **Flutter:** Android: single `Activity`. iOS: `FlutterViewController` hosts Flutter's navigator.
