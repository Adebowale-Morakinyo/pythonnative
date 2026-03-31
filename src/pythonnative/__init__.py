"""PythonNative — declarative native UI for Android and iOS.

Public API::

    import pythonnative as pn

    class MainPage(pn.Page):
        def __init__(self, native_instance):
            super().__init__(native_instance)
            self.state = {"count": 0}

        def render(self):
            return pn.Column(
                pn.Text(f"Count: {self.state['count']}", font_size=24),
                pn.Button("Increment", on_click=lambda: self.set_state(count=self.state["count"] + 1)),
                spacing=12,
            )
"""

__version__ = "0.4.0"

from .components import (
    ActivityIndicator,
    Button,
    Column,
    Image,
    ProgressBar,
    Row,
    ScrollView,
    Spacer,
    Switch,
    Text,
    TextInput,
    WebView,
)
from .element import Element
from .page import Page

__all__ = [
    "ActivityIndicator",
    "Button",
    "Column",
    "Element",
    "Image",
    "Page",
    "ProgressBar",
    "Row",
    "ScrollView",
    "Spacer",
    "Switch",
    "Text",
    "TextInput",
    "WebView",
]
