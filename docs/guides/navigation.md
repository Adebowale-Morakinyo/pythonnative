# Navigation

PythonNative offers two approaches to navigation:

1. **Declarative navigators** (recommended) — component-based, inspired by React Navigation
2. **Legacy push/pop** — imperative navigation via `use_navigation()`

## Declarative Navigation

Declarative navigators manage screen state as components. Define your screens once, and the navigator handles rendering, transitions, and state.

### Stack Navigator

A stack navigator manages a stack of screens — push to go forward, pop to go back.

```python
import pythonnative as pn
from pythonnative.navigation import NavigationContainer, create_stack_navigator

Stack = create_stack_navigator()

@pn.component
def App():
    return NavigationContainer(
        Stack.Navigator(
            Stack.Screen("Home", component=HomeScreen),
            Stack.Screen("Detail", component=DetailScreen),
            initial_route="Home",
        )
    )

@pn.component
def HomeScreen():
    nav = pn.use_navigation()
    return pn.Column(
        pn.Text("Home", style={"font_size": 24}),
        pn.Button(
            "Go to Detail",
            on_click=lambda: nav.navigate("Detail", params={"id": 42}),
        ),
        style={"spacing": 12, "padding": 16},
    )

@pn.component
def DetailScreen():
    nav = pn.use_navigation()
    params = nav.get_params()
    return pn.Column(
        pn.Text(f"Detail #{params.get('id')}", style={"font_size": 20}),
        pn.Button("Back", on_click=nav.go_back),
        style={"spacing": 12, "padding": 16},
    )
```

### Tab Navigator

A tab navigator renders a tab bar and switches between screens.

```python
from pythonnative.navigation import create_tab_navigator

Tab = create_tab_navigator()

@pn.component
def App():
    return NavigationContainer(
        Tab.Navigator(
            Tab.Screen("Home", component=HomeScreen, options={"title": "Home"}),
            Tab.Screen("Settings", component=SettingsScreen, options={"title": "Settings"}),
        )
    )
```

### Drawer Navigator

A drawer navigator provides a side menu for switching screens.

```python
from pythonnative.navigation import create_drawer_navigator

Drawer = create_drawer_navigator()

@pn.component
def App():
    return NavigationContainer(
        Drawer.Navigator(
            Drawer.Screen("Home", component=HomeScreen, options={"title": "Home"}),
            Drawer.Screen("Profile", component=ProfileScreen, options={"title": "Profile"}),
        )
    )

@pn.component
def HomeScreen():
    nav = pn.use_navigation()
    return pn.Column(
        pn.Button("Open Menu", on_click=nav.open_drawer),
        pn.Text("Home Screen"),
    )
```

### Nesting Navigators

Navigators can be nested — for example, tabs containing stacks:

```python
Stack = create_stack_navigator()
Tab = create_tab_navigator()

@pn.component
def HomeStack():
    return Stack.Navigator(
        Stack.Screen("Feed", component=FeedScreen),
        Stack.Screen("Post", component=PostScreen),
    )

@pn.component
def App():
    return NavigationContainer(
        Tab.Navigator(
            Tab.Screen("Home", component=HomeStack, options={"title": "Home"}),
            Tab.Screen("Settings", component=SettingsScreen, options={"title": "Settings"}),
        )
    )
```

## NavigationHandle API

Inside any screen rendered by a navigator, `pn.use_navigation()` returns a handle with:

- **`.navigate(route_name, params=...)`** — navigate to a named route with optional params
- **`.go_back()`** — pop the current screen
- **`.get_params()`** — get the current route's params dict
- **`.reset(route_name, params=...)`** — reset the stack to a single route

### Drawer-specific methods

When inside a drawer navigator, the handle also provides:

- **`.open_drawer()`** — open the drawer
- **`.close_drawer()`** — close the drawer
- **`.toggle_drawer()`** — toggle the drawer open/closed

## Focus-aware Effects

Use `pn.use_focus_effect()` to run effects only when a screen is focused:

```python
@pn.component
def DataScreen():
    data, set_data = pn.use_state(None)

    pn.use_focus_effect(lambda: fetch_data(set_data), [])

    return pn.Text(f"Data: {data}")
```

## Route Parameters

Use `pn.use_route()` for convenient access to route params:

```python
@pn.component
def DetailScreen():
    params = pn.use_route()
    item_id = params.get("id", 0)
    return pn.Text(f"Item #{item_id}")
```

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
