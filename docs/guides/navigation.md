# Navigation

This guide shows how to navigate between screens and pass data using the `use_navigation()` hook.

## Push / Pop

Call `pn.use_navigation()` inside a `@pn.component` to get a `NavigationHandle`. Use `.push()` and `.pop()` to change screens, passing a component reference with optional `args`.

```python
import pythonnative as pn
from app.second_page import SecondPage


@pn.component
def HomeScreen():
    nav = pn.use_navigation()
    return pn.Column(
        pn.Text("Home", style={"font_size": 24}),
        pn.Button(
            "Go next",
            on_click=lambda: nav.push(
                SecondPage,
                args={"message": "Hello from Home"},
            ),
        ),
        style={"spacing": 12, "padding": 16},
    )
```

On the target screen, retrieve args with `nav.get_args()`:

```python
@pn.component
def SecondPage():
    nav = pn.use_navigation()
    message = nav.get_args().get("message", "Second Page")
    return pn.Column(
        pn.Text(message, style={"font_size": 20}),
        pn.Button("Back", on_click=nav.pop),
        style={"spacing": 12, "padding": 16},
    )
```

## NavigationHandle API

`pn.use_navigation()` returns a `NavigationHandle` with:

- **`.push(component, args=...)`** — navigate to a new screen. Pass a component reference (the `@pn.component` function itself), with an optional `args` dict.
- **`.pop()`** — go back to the previous screen.
- **`.get_args()`** — retrieve the args dict passed by the caller.

## Lifecycle

PythonNative forwards lifecycle events from the host:

- `on_create` — triggers the initial render
- `on_start`
- `on_resume`
- `on_pause`
- `on_stop`
- `on_destroy`
- `on_restart` (Android only)
- `on_save_instance_state`
- `on_restore_instance_state`

## Notes

- On Android, `push` navigates via `NavController` to a `PageFragment` and passes `page_path` and optional JSON `args`.
- On iOS, `push` uses the root `UINavigationController` to push a new `ViewController` and passes page info via KVC.

## Platform specifics

### iOS (UIViewController per page)
- Each PythonNative screen is hosted by a Swift `ViewController` instance.
- Screens are pushed and popped on a root `UINavigationController`.
- Lifecycle is forwarded from Swift to the registered Python component.

### Android (single Activity, Fragment stack)
- Single host `MainActivity` sets a `NavHostFragment` containing a navigation graph.
- Each PythonNative screen is represented by a generic `PageFragment` which instantiates the Python component and attaches its root view.
- `push`/`pop` delegate to `NavController` (via a small `Navigator` helper).
- Arguments live in Fragment arguments and restore across configuration changes.

## Comparison to other frameworks
- **React Native:** Android: single `Activity`, screens managed via `Fragment`s. iOS: screens map to `UIViewController`s pushed on `UINavigationController`.
- **NativeScript:** Android: single `Activity`, pages as `Fragment`s. iOS: pages as `UIViewController`s on `UINavigationController`.
- **Flutter:** Android: single `Activity`. iOS: `FlutterViewController` hosts Flutter's navigator.
