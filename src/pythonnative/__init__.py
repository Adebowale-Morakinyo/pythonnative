"""PythonNative: declarative native UI for Android and iOS.

PythonNative is a cross-platform toolkit that turns Python ``@component``
functions into real, native Android and iOS views. The component model
is React-like (function components plus hooks), but rendering happens
through direct platform bindings: Chaquopy on Android (Java) and
rubicon-objc on iOS (Objective-C). There is no JavaScript bridge.

Key building blocks:

- **Element factories** ([`Text`][pythonnative.Text],
  [`Button`][pythonnative.Button], [`Column`][pythonnative.Column], etc.)
  return immutable [`Element`][pythonnative.Element] descriptors.
- **Hooks** ([`use_state`][pythonnative.use_state],
  [`use_effect`][pythonnative.use_effect],
  [`use_reducer`][pythonnative.use_reducer], etc.) manage state, side
  effects, and context inside `@component` functions.
- **Navigation** is built from
  [`NavigationContainer`][pythonnative.NavigationContainer] plus one of
  the [`create_stack_navigator`][pythonnative.create_stack_navigator],
  [`create_tab_navigator`][pythonnative.create_tab_navigator], or
  [`create_drawer_navigator`][pythonnative.create_drawer_navigator]
  factories.
- **Styling** uses a single ``style`` dict per element (or a list of
  dicts), composable via [`StyleSheet`][pythonnative.StyleSheet].

Example:
    ```python
    import pythonnative as pn

    @pn.component
    def App():
        count, set_count = pn.use_state(0)
        return pn.Column(
            pn.Text(f"Count: {count}", style={"font_size": 24}),
            pn.Button("+", on_click=lambda: set_count(count + 1)),
            style={"spacing": 12},
        )
    ```
"""

__version__ = "0.11.0"

from .components import (
    ActivityIndicator,
    Button,
    Column,
    ErrorBoundary,
    FlatList,
    Image,
    Modal,
    Pressable,
    ProgressBar,
    Row,
    SafeAreaView,
    ScrollView,
    Slider,
    Spacer,
    Switch,
    Text,
    TextInput,
    View,
    WebView,
)
from .element import Element
from .hooks import (
    Provider,
    batch_updates,
    component,
    create_context,
    use_callback,
    use_context,
    use_effect,
    use_memo,
    use_navigation,
    use_reducer,
    use_ref,
    use_state,
)
from .navigation import (
    NavigationContainer,
    create_drawer_navigator,
    create_stack_navigator,
    create_tab_navigator,
    use_focus_effect,
    use_route,
)
from .page import create_page
from .style import StyleSheet, ThemeContext

__all__ = [
    # Components
    "ActivityIndicator",
    "Button",
    "Column",
    "ErrorBoundary",
    "FlatList",
    "Image",
    "Modal",
    "Pressable",
    "ProgressBar",
    "Row",
    "SafeAreaView",
    "ScrollView",
    "Slider",
    "Spacer",
    "Switch",
    "Text",
    "TextInput",
    "View",
    "WebView",
    # Core
    "Element",
    "create_page",
    # Hooks
    "batch_updates",
    "component",
    "create_context",
    "use_callback",
    "use_context",
    "use_effect",
    "use_focus_effect",
    "use_memo",
    "use_navigation",
    "use_reducer",
    "use_ref",
    "use_route",
    "use_state",
    "Provider",
    # Navigation
    "NavigationContainer",
    "create_drawer_navigator",
    "create_stack_navigator",
    "create_tab_navigator",
    # Styling
    "StyleSheet",
    "ThemeContext",
]
