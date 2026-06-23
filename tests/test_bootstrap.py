"""Tests for the root-entry resolver used by the native templates."""

import sys
import types
from typing import Any, List, Optional, Tuple

import pytest

from pythonnative import bootstrap
from pythonnative import screen as screen_mod


def _fake_pn_entry(entry_module: str, dev_client: bool) -> types.ModuleType:
    module = types.ModuleType("pn_entry")
    module.ENTRY_MODULE = entry_module  # type: ignore[attr-defined]
    module.DEV_CLIENT = dev_client  # type: ignore[attr-defined]
    return module


def test_root_entry_module_defaults_without_marker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delitem(sys.modules, "pn_entry", raising=False)
    # With no importable pn_entry, the resolver falls back to the default.
    assert bootstrap.root_entry_module() == bootstrap.DEFAULT_ENTRY


def test_root_entry_module_reads_marker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "pn_entry", _fake_pn_entry("my.app.entry", False))
    assert bootstrap.root_entry_module() == "my.app.entry"


def test_root_entry_module_dev_client_uses_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "pn_entry", _fake_pn_entry("ignored", True))
    assert bootstrap.root_entry_module() == screen_mod.DEV_CLIENT_ENTRY


def test_create_root_host_mounts_entry_component(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: List[Tuple[str, Any, Optional[str]]] = []

    def fake_create_screen(path: str, native: Any = None, args: Optional[str] = None) -> str:
        calls.append((path, native, args))
        return "entry-host"

    monkeypatch.setitem(sys.modules, "pn_entry", _fake_pn_entry("app.main", False))
    monkeypatch.setattr(screen_mod, "create_screen", fake_create_screen)

    host = bootstrap.create_root_host("native", "{}")
    assert host == "entry-host"
    assert calls == [("app.main", "native", "{}")]


def test_create_root_host_mounts_dev_client(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: List[Any] = []

    def fake_dev_host(native: Any = None, args: Optional[str] = None) -> str:
        calls.append((native, args))
        return "dev-host"

    monkeypatch.setitem(sys.modules, "pn_entry", _fake_pn_entry("ignored", True))
    monkeypatch.setattr(screen_mod, "create_dev_client_host", fake_dev_host)

    host = bootstrap.create_root_host("native", None)
    assert host == "dev-host"
    assert calls == [("native", None)]
