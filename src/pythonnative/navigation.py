"""Declarative navigation for PythonNative.

Provides a component-based navigation system inspired by React Navigation.
Navigators manage screen state in Python; they render the active screen's
component using the standard reconciler pipeline.

Usage::

    from pythonnative.navigation import (
        NavigationContainer,
        create_stack_navigator,
        create_tab_navigator,
        create_drawer_navigator,
    )

    Stack = create_stack_navigator()

    @pn.component
    def App():
        return NavigationContainer(
            Stack.Navigator(
                Stack.Screen("Home", component=HomeScreen),
                Stack.Screen("Detail", component=DetailScreen),
            )
        )
"""

from typing import Any, Callable, Dict, List, Optional

from .element import Element
from .hooks import (
    Provider,
    _NavigationContext,
    component,
    create_context,
    use_context,
    use_effect,
    use_memo,
    use_ref,
    use_state,
)

# ======================================================================
# Focus context
# ======================================================================

_FocusContext = create_context(False)

# ======================================================================
# Data structures
# ======================================================================


class _ScreenDef:
    """Configuration for a single screen within a navigator."""

    __slots__ = ("name", "component", "options")

    def __init__(self, name: str, component_fn: Any, options: Optional[Dict[str, Any]] = None) -> None:
        self.name = name
        self.component = component_fn
        self.options = options or {}

    def __repr__(self) -> str:
        return f"Screen({self.name!r})"


class _RouteEntry:
    """An entry in the navigation stack."""

    __slots__ = ("name", "params")

    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None) -> None:
        self.name = name
        self.params = params or {}

    def __repr__(self) -> str:
        return f"Route({self.name!r})"


# ======================================================================
# Navigation handle for declarative navigators
# ======================================================================


class _DeclarativeNavHandle:
    """Navigation handle provided by declarative navigators.

    Implements the same interface as :class:`~pythonnative.hooks.NavigationHandle`
    so that ``use_navigation()`` returns a compatible object regardless of
    whether the app uses the legacy page-based navigation or declarative
    navigators.

    When *parent* is provided, unknown routes and root-level ``go_back``
    calls are forwarded to the parent handle.  This enables nested
    navigators (e.g. a stack inside a tab) to delegate navigation actions
    that they cannot handle locally.
    """

    def __init__(
        self,
        screen_map: Dict[str, "_ScreenDef"],
        get_stack: Callable[[], List["_RouteEntry"]],
        set_stack: Callable,
        parent: Any = None,
    ) -> None:
        self._screen_map = screen_map
        self._get_stack = get_stack
        self._set_stack = set_stack
        self._parent = parent

    def navigate(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Navigate to a named route, pushing it onto the stack.

        If *route_name* is not known locally and a parent handle exists,
        the call is forwarded to the parent navigator.
        """
        if route_name in self._screen_map:
            entry = _RouteEntry(route_name, params)
            self._set_stack(lambda s: list(s) + [entry])
        elif self._parent is not None:
            self._parent.navigate(route_name, params=params)
        else:
            raise ValueError(f"Unknown route: {route_name!r}. Known routes: {list(self._screen_map)}")

    def go_back(self) -> None:
        """Pop the current screen from the stack.

        If the stack is at its root and a parent handle exists, the call
        is forwarded to the parent navigator.
        """
        stack = self._get_stack()
        if len(stack) > 1:
            self._set_stack(lambda s: list(s[:-1]))
        elif self._parent is not None:
            self._parent.go_back()

    def get_params(self) -> Dict[str, Any]:
        """Return the parameters for the current route."""
        stack = self._get_stack()
        return stack[-1].params if stack else {}

    def reset(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Reset the stack to a single route."""
        if route_name not in self._screen_map:
            raise ValueError(f"Unknown route: {route_name!r}. Known routes: {list(self._screen_map)}")
        self._set_stack([_RouteEntry(route_name, params)])


class _TabNavHandle(_DeclarativeNavHandle):
    """Navigation handle for tab navigators with tab switching."""

    def __init__(
        self,
        screen_map: Dict[str, "_ScreenDef"],
        get_stack: Callable[[], List["_RouteEntry"]],
        set_stack: Callable,
        switch_tab: Callable[[str, Optional[Dict[str, Any]]], None],
        parent: Any = None,
    ) -> None:
        super().__init__(screen_map, get_stack, set_stack, parent=parent)
        self._switch_tab = switch_tab

    def navigate(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Switch to a tab by name, or forward to parent for unknown routes."""
        if route_name in self._screen_map:
            self._switch_tab(route_name, params)
        elif self._parent is not None:
            self._parent.navigate(route_name, params=params)
        else:
            raise ValueError(f"Unknown route: {route_name!r}. Known routes: {list(self._screen_map)}")


class _DrawerNavHandle(_DeclarativeNavHandle):
    """Navigation handle for drawer navigators with open/close control."""

    def __init__(
        self,
        screen_map: Dict[str, "_ScreenDef"],
        get_stack: Callable[[], List["_RouteEntry"]],
        set_stack: Callable,
        switch_screen: Callable[[str, Optional[Dict[str, Any]]], None],
        set_drawer_open: Callable[[bool], None],
        get_drawer_open: Callable[[], bool],
        parent: Any = None,
    ) -> None:
        super().__init__(screen_map, get_stack, set_stack, parent=parent)
        self._switch_screen = switch_screen
        self._set_drawer_open = set_drawer_open
        self._get_drawer_open = get_drawer_open

    def navigate(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Switch to a screen and close the drawer, or forward to parent."""
        if route_name in self._screen_map:
            self._switch_screen(route_name, params)
            self._set_drawer_open(False)
        elif self._parent is not None:
            self._parent.navigate(route_name, params=params)
        else:
            raise ValueError(f"Unknown route: {route_name!r}. Known routes: {list(self._screen_map)}")

    def open_drawer(self) -> None:
        """Open the drawer."""
        self._set_drawer_open(True)

    def close_drawer(self) -> None:
        """Close the drawer."""
        self._set_drawer_open(False)

    def toggle_drawer(self) -> None:
        """Toggle the drawer open/closed."""
        self._set_drawer_open(not self._get_drawer_open())


# ======================================================================
# Stack navigator
# ======================================================================


def _build_screen_map(screens: Any) -> Dict[str, "_ScreenDef"]:
    """Build an ordered dict of name -> _ScreenDef from a list."""
    result: Dict[str, _ScreenDef] = {}
    for s in screens or []:
        if isinstance(s, _ScreenDef):
            result[s.name] = s
    return result


@component
def _stack_navigator_impl(screens: Any = None, initial_route: Optional[str] = None) -> Element:
    screen_map = _build_screen_map(screens)
    if not screen_map:
        return Element("View", {}, [])

    parent_nav = use_context(_NavigationContext)

    first_route = initial_route or next(iter(screen_map))
    stack, set_stack = use_state(lambda: [_RouteEntry(first_route)])

    stack_ref = use_ref(None)
    stack_ref["current"] = stack

    handle = use_memo(
        lambda: _DeclarativeNavHandle(screen_map, lambda: stack_ref["current"], set_stack, parent=parent_nav), []
    )
    handle._screen_map = screen_map
    handle._parent = parent_nav

    current = stack[-1]
    screen_def = screen_map.get(current.name)
    if screen_def is None:
        return Element("Text", {"text": f"Unknown route: {current.name}"}, [])

    screen_el = screen_def.component()
    return Provider(_NavigationContext, handle, Provider(_FocusContext, True, screen_el))


def create_stack_navigator() -> Any:
    """Create a stack-based navigator.

    Returns an object with ``Navigator`` and ``Screen`` members::

        Stack = create_stack_navigator()

        Stack.Screen("Home", component=HomeScreen)

        Stack.Navigator(
            Stack.Screen("Home", component=HomeScreen),
            Stack.Screen("Detail", component=DetailScreen),
            initial_route="Home",
        )
    """

    class _StackNavigator:
        @staticmethod
        def Screen(name: str, *, component: Any, options: Optional[Dict[str, Any]] = None) -> "_ScreenDef":
            """Define a screen within this stack navigator."""
            return _ScreenDef(name, component, options)

        @staticmethod
        def Navigator(*screens: Any, initial_route: Optional[str] = None, key: Optional[str] = None) -> Element:
            """Render the stack navigator with the given screens."""
            return _stack_navigator_impl(screens=list(screens), initial_route=initial_route, key=key)

    return _StackNavigator()


# ======================================================================
# Tab navigator
# ======================================================================


@component
def _tab_navigator_impl(screens: Any = None, initial_route: Optional[str] = None) -> Element:
    screen_list = list(screens or [])
    screen_map = _build_screen_map(screen_list)
    if not screen_map:
        return Element("View", {}, [])

    parent_nav = use_context(_NavigationContext)

    first_route = initial_route or screen_list[0].name
    active_tab, set_active_tab = use_state(first_route)
    tab_params, set_tab_params = use_state(lambda: {first_route: {}})

    params_ref = use_ref(None)
    params_ref["current"] = tab_params

    def switch_tab(name: str, params: Optional[Dict[str, Any]] = None) -> None:
        set_active_tab(name)
        if params:
            set_tab_params(lambda p: {**p, name: params})

    def get_stack() -> List[_RouteEntry]:
        p = params_ref["current"] or {}
        return [_RouteEntry(active_tab, p.get(active_tab, {}))]

    handle = use_memo(lambda: _TabNavHandle(screen_map, get_stack, lambda _: None, switch_tab, parent=parent_nav), [])
    handle._screen_map = screen_map
    handle._switch_tab = switch_tab
    handle._parent = parent_nav

    screen_def = screen_map.get(active_tab)
    if screen_def is None:
        screen_def = screen_map[screen_list[0].name]

    tab_items: List[Dict[str, str]] = []
    for s in screen_list:
        if isinstance(s, _ScreenDef):
            tab_items.append({"name": s.name, "title": s.options.get("title", s.name)})

    def on_tab_select(name: str) -> None:
        switch_tab(name)

    tab_bar = Element(
        "TabBar",
        {"items": tab_items, "active_tab": active_tab, "on_tab_select": on_tab_select},
        [],
        key="__tab_bar__",
    )

    screen_el = screen_def.component()
    content = Provider(
        _NavigationContext,
        handle,
        Provider(_FocusContext, True, screen_el),
    )

    return Element(
        "View",
        {"flex_direction": "column", "flex": 1},
        [Element("View", {"flex": 1}, [content]), tab_bar],
    )


def create_tab_navigator() -> Any:
    """Create a tab-based navigator.

    Returns an object with ``Navigator`` and ``Screen`` members::

        Tab = create_tab_navigator()

        Tab.Navigator(
            Tab.Screen("Home", component=HomeScreen, options={"title": "Home"}),
            Tab.Screen("Settings", component=SettingsScreen),
        )
    """

    class _TabNavigator:
        @staticmethod
        def Screen(name: str, *, component: Any, options: Optional[Dict[str, Any]] = None) -> "_ScreenDef":
            """Define a screen within this tab navigator."""
            return _ScreenDef(name, component, options)

        @staticmethod
        def Navigator(*screens: Any, initial_route: Optional[str] = None, key: Optional[str] = None) -> Element:
            """Render the tab navigator with the given screens."""
            return _tab_navigator_impl(screens=list(screens), initial_route=initial_route, key=key)

    return _TabNavigator()


# ======================================================================
# Drawer navigator
# ======================================================================


@component
def _drawer_navigator_impl(screens: Any = None, initial_route: Optional[str] = None) -> Element:
    screen_list = list(screens or [])
    screen_map = _build_screen_map(screen_list)
    if not screen_map:
        return Element("View", {}, [])

    parent_nav = use_context(_NavigationContext)

    first_route = initial_route or screen_list[0].name
    active_screen, set_active_screen = use_state(first_route)
    drawer_open, set_drawer_open = use_state(False)
    screen_params, set_screen_params = use_state(lambda: {first_route: {}})

    params_ref = use_ref(None)
    params_ref["current"] = screen_params

    def switch_screen(name: str, params: Optional[Dict[str, Any]] = None) -> None:
        set_active_screen(name)
        if params:
            set_screen_params(lambda p: {**p, name: params})

    def get_stack() -> List[_RouteEntry]:
        p = params_ref["current"] or {}
        return [_RouteEntry(active_screen, p.get(active_screen, {}))]

    handle = use_memo(
        lambda: _DrawerNavHandle(
            screen_map,
            get_stack,
            lambda _: None,
            switch_screen,
            set_drawer_open,
            lambda: drawer_open,
            parent=parent_nav,
        ),
        [],
    )
    handle._screen_map = screen_map
    handle._switch_screen = switch_screen
    handle._set_drawer_open = set_drawer_open
    handle._get_drawer_open = lambda: drawer_open
    handle._parent = parent_nav

    screen_def = screen_map.get(active_screen)
    if screen_def is None:
        screen_def = screen_map[screen_list[0].name]

    screen_el = screen_def.component()
    content = Provider(
        _NavigationContext,
        handle,
        Provider(_FocusContext, True, screen_el),
    )

    children: List[Element] = [Element("View", {"flex": 1}, [content])]

    if drawer_open:
        menu_items: List[Element] = []
        for s in screen_list:
            if not isinstance(s, _ScreenDef):
                continue
            label = s.options.get("title", s.name)
            item_name = s.name

            def make_select(n: str) -> Callable[[], None]:
                def _select() -> None:
                    switch_screen(n)
                    set_drawer_open(False)

                return _select

            menu_items.append(
                Element("Button", {"title": label, "on_click": make_select(item_name)}, [], key=f"__drawer_{item_name}")
            )

        drawer_panel = Element(
            "View",
            {"background_color": "#FFFFFF", "width": 250},
            menu_items,
        )
        children.insert(0, drawer_panel)

    return Element("View", {"flex_direction": "row", "flex": 1}, children)


def create_drawer_navigator() -> Any:
    """Create a drawer-based navigator.

    Returns an object with ``Navigator`` and ``Screen`` members::

        Drawer = create_drawer_navigator()

        Drawer.Navigator(
            Drawer.Screen("Home", component=HomeScreen, options={"title": "Home"}),
            Drawer.Screen("Settings", component=SettingsScreen),
        )

    The navigation handle returned by ``use_navigation()`` inside a drawer
    navigator includes ``open_drawer()``, ``close_drawer()``, and
    ``toggle_drawer()`` methods.
    """

    class _DrawerNavigator:
        @staticmethod
        def Screen(name: str, *, component: Any, options: Optional[Dict[str, Any]] = None) -> "_ScreenDef":
            """Define a screen within this drawer navigator."""
            return _ScreenDef(name, component, options)

        @staticmethod
        def Navigator(*screens: Any, initial_route: Optional[str] = None, key: Optional[str] = None) -> Element:
            """Render the drawer navigator with the given screens."""
            return _drawer_navigator_impl(screens=list(screens), initial_route=initial_route, key=key)

    return _DrawerNavigator()


# ======================================================================
# NavigationContainer
# ======================================================================


def NavigationContainer(child: Element, *, key: Optional[str] = None) -> Element:
    """Root container for the navigation tree.

    Wraps the child navigator in a full-size view. All declarative
    navigators (stack, tab, drawer) should be nested inside a
    ``NavigationContainer``::

        @pn.component
        def App():
            return NavigationContainer(
                Stack.Navigator(
                    Stack.Screen("Home", component=HomeScreen),
                )
            )
    """
    return Element("View", {"flex": 1}, [child], key=key)


# ======================================================================
# Hooks
# ======================================================================


def use_route() -> Dict[str, Any]:
    """Return the current route's parameters.

    Convenience hook that reads from the navigation context::

        @pn.component
        def DetailScreen():
            params = pn.use_route()
            item_id = params.get("id")
            ...
    """
    nav = use_context(_NavigationContext)
    if nav is None:
        return {}
    get_params = getattr(nav, "get_params", None)
    if get_params:
        return get_params()
    return {}


def use_focus_effect(effect: Callable, deps: Optional[list] = None) -> None:
    """Run *effect* only when the screen is focused.

    Like ``use_effect`` but skips execution when the screen is not the
    active/focused screen in a navigator::

        @pn.component
        def HomeScreen():
            pn.use_focus_effect(lambda: print("screen focused"), [])
    """
    is_focused = use_context(_FocusContext)
    all_deps = [is_focused] + (list(deps) if deps is not None else [])

    def wrapped_effect() -> Any:
        if is_focused:
            return effect()
        return None

    use_effect(wrapped_effect, all_deps)
