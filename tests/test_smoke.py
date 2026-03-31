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
    }
    assert expected.issubset(set(pn.__all__))
