"""Verify the package is importable and exports the public API."""

import pythonnative as pn
from pythonnative.element import Element


def test_package_version() -> None:
    assert pn.__version__


def test_element_class_exported() -> None:
    assert pn.Element is Element


def test_public_api_names() -> None:
    expected = {
        "ActivityIndicator",
        "Button",
        "Column",
        "Element",
        "FlatList",
        "Image",
        "Modal",
        "Page",
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
    }
    assert expected.issubset(set(pn.__all__))
