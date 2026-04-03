"""PythonNative — declarative native UI for Android and iOS.

Public API::

    import pythonnative as pn

    @pn.component
    def counter(initial=0):
        count, set_count = pn.use_state(initial)
        return pn.Column(
            pn.Text(f"Count: {count}", font_size=24),
            pn.Button("+", on_click=lambda: set_count(count + 1)),
            spacing=12,
        )

    class MainPage(pn.Page):
        def __init__(self, native_instance):
            super().__init__(native_instance)

        def render(self):
            return pn.Column(
                counter(initial=0),
                counter(initial=10),
                spacing=16,
                padding=16,
            )
"""

__version__ = "0.5.0"

from .components import (
    ActivityIndicator,
    Button,
    Column,
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
    component,
    create_context,
    use_callback,
    use_context,
    use_effect,
    use_memo,
    use_ref,
    use_state,
)
from .page import Page
from .style import StyleSheet, ThemeContext

__all__ = [
    # Components
    "ActivityIndicator",
    "Button",
    "Column",
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
    "Page",
    # Hooks
    "component",
    "create_context",
    "use_callback",
    "use_context",
    "use_effect",
    "use_memo",
    "use_ref",
    "use_state",
    "Provider",
    # Styling
    "StyleSheet",
    "ThemeContext",
]
