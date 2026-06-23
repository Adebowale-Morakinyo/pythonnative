"""Tests for the dev-client hooks added to the screen host."""

import os
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

import pythonnative.screen as screen_mod
from pythonnative.native_views import NativeViewRegistry
from pythonnative.native_views.base import ViewHandler
from pythonnative.screen import create_dev_client_host, create_screen, mount_component


class _StubView:
    def __init__(self, props: Dict[str, Any]) -> None:
        self.props = dict(props)


class _TextHandler(ViewHandler):
    def create(self, tag: int, props: Dict[str, Any]) -> _StubView:
        return _StubView(props)

    def update(self, native_view: _StubView, changed_props: Dict[str, Any]) -> None:
        native_view.props.update(changed_props)


def _write_component(path: Path, text: str) -> None:
    path.write_text(
        "from pythonnative.element import Element\n\n"
        "def Root():\n"
        f"    return Element('Text', {{'text': {text!r}}}, [])\n",
        encoding="utf-8",
    )


def test_mount_component_repoints_live_host(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = tmp_path / "mount_app"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    _write_component(package / "a.py", "A")
    _write_component(package / "b.py", "B")

    monkeypatch.syspath_prepend(os.fspath(tmp_path))
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    for name in ("mount_app", "mount_app.a", "mount_app.b"):
        sys.modules.pop(name, None)

    registry = NativeViewRegistry()
    registry.register("Text", _TextHandler())
    import pythonnative.native_views as native_views

    monkeypatch.setattr(native_views, "_registry", registry)

    host: Any = create_screen("mount_app.a.Root")
    host.on_create()
    assert host._root_native_view.props["text"] == "A"

    mount_component(host, "mount_app.b.Root")
    assert host._component_path == "mount_app.b.Root"
    assert host._root_native_view.props["text"] == "B"


def test_create_dev_client_host_attaches_session(monkeypatch: pytest.MonkeyPatch) -> None:
    from pythonnative.dev import session as session_mod

    sentinel = object()
    monkeypatch.setattr(screen_mod, "create_screen", lambda *a, **k: sentinel)
    session_mod.reset_session()
    try:
        host = create_dev_client_host("native", None)
        assert host is sentinel
        assert session_mod.get_session()._host is sentinel
    finally:
        session_mod.reset_session()
