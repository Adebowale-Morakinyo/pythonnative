"""Tests for page-host lifecycle behavior."""

import os
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

from pythonnative.native_views import NativeViewRegistry
from pythonnative.native_views.base import ViewHandler
from pythonnative.page import create_page


class StubView:
    """Small native-view stand-in used by page-host tests."""

    def __init__(self, props: Dict[str, Any]) -> None:
        self.props = dict(props)


class TextHandler(ViewHandler):
    """Minimal text handler for mounting page roots on desktop."""

    def create(self, props: Dict[str, Any]) -> StubView:
        return StubView(props)

    def update(self, native_view: StubView, changed_props: Dict[str, Any]) -> None:
        native_view.props.update(changed_props)


def _write_screen(path: Path, text: str) -> None:
    path.write_text(
        "from pythonnative.element import Element\n\n"
        "def MainPage():\n"
        f"    return Element('Text', {{'text': {text!r}}}, [])\n",
        encoding="utf-8",
    )


def test_page_reload_reimports_root_component(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_dir = tmp_path / "reload_app"
    package_dir.mkdir()
    screen_path = package_dir / "screen.py"
    _write_screen(screen_path, "before")

    monkeypatch.syspath_prepend(os.fspath(tmp_path))
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    sys.modules.pop("reload_app.screen", None)
    sys.modules.pop("reload_app", None)

    registry = NativeViewRegistry()
    registry.register("Text", TextHandler())
    import pythonnative.native_views as native_views

    monkeypatch.setattr(native_views, "_registry", registry)

    host: Any = create_page("reload_app.screen.MainPage")
    host.on_create()
    assert host._root_native_view.props["text"] == "before"

    _write_screen(screen_path, "after")
    host.reload(["reload_app.screen"])

    assert host._root_native_view.props["text"] == "after"
