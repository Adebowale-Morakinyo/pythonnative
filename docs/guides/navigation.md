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

Android uses a single `MainActivity` hosting a `NavHostFragment` and a generic `PageFragment` per page. iOS forwards `viewWillAppear`/`viewWillDisappear` via an internal registry.

## Notes

- On Android, `push` navigates via `NavController` to a `PageFragment` and passes `page_path` and optional JSON `args`.
- On iOS, `push` uses the root `UINavigationController` to push a new `ViewController` and passes page info via KVC.

## Platform specifics

### iOS (UIViewController per page)
- Each PythonNative page is hosted by a Swift `ViewController` instance.
- Pages are pushed and popped on a root `UINavigationController`.
- Lifecycle is forwarded from Swift to the registered Python page instance.
- Root view wiring: `Page.set_root_view` sizes and inserts the Python-native view into the controller’s view.

Why this matches iOS conventions
- iOS apps commonly model screens as `UIViewController`s and use `UINavigationController` for hierarchical navigation.
- The approach integrates cleanly with add-to-app and system behaviors (e.g., state restoration).

### Android (single Activity, Fragment stack)
- Single host `MainActivity` sets a `NavHostFragment` containing a navigation graph.
- Each PythonNative page is represented by a generic `PageFragment` which instantiates the Python page and attaches its root view.
- `push`/`pop` delegate to `NavController` (via a small `Navigator` helper).
- Arguments (`page_path`, `args_json`) live in Fragment arguments and restore across configuration changes and process death.

Why this matches Android conventions
- Modern Android apps favor one Activity with many Fragments, using Jetpack Navigation for back stack, transitions, and deep links.
- It simplifies lifecycle, back handling, and state compared to one-Activity-per-screen.

## Comparison to other frameworks
- React Native
  - Android: single `Activity`, screens managed via `Fragment`s (e.g., `react-native-screens`).
  - iOS: screens map to `UIViewController`s pushed on `UINavigationController`.
- .NET MAUI / Xamarin.Forms
  - Android: single `Activity`, pages via Fragments/Navigation.
  - iOS: pages map to `UIViewController`s on a `UINavigationController`.
- NativeScript
  - Android: single `Activity`, pages as `Fragment`s.
  - iOS: pages as `UIViewController`s on `UINavigationController`.
- Flutter (special case)
  - Android: single `Activity` (`FlutterActivity`/`FlutterFragmentActivity`).
  - iOS: `FlutterViewController` hosts Flutter’s internal navigator; add-to-app can push multiple `FlutterViewController`s.

Bottom line
- iOS: one host VC class, many instances on a `UINavigationController`.
- Android: one host `Activity`, many `Fragment`s with Jetpack Navigation.
