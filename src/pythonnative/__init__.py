"""PythonNative — declarative native UI for Android and iOS.

Public API::

    import pythonnative as pn

    @pn.component
    def App():
        count, set_count = pn.use_state(0)
        return pn.Column(
            pn.Text(f"Count: {count}", style={"font_size": 24}),
            pn.Button("+", on_click=lambda: set_count(count + 1)),
            style={"spacing": 12},
        )
"""

__version__ = "0.8.0"

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
