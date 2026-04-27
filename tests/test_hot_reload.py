"""Tests for hot-reload source overlays and manifest handling."""

import importlib
import json
import os
import sys
from pathlib import Path

import pytest

from pythonnative.hot_reload import (
    DEV_ROOT_DIR,
    ModuleReloader,
    configure_dev_environment,
    manifest_path_for,
)


def _write_module(path: Path, value: str) -> None:
    path.write_text(f"VALUE = {value!r}\n", encoding="utf-8")


def test_configure_dev_environment_prioritizes_overlay(tmp_path: Path) -> None:
    writable_root = os.fspath(tmp_path)
    dev_root = configure_dev_environment(writable_root)

    assert dev_root == os.path.join(writable_root, DEV_ROOT_DIR)
    assert os.path.isdir(os.path.join(dev_root, "app"))
    assert sys.path[0] == dev_root


def test_file_to_module_normalizes_relative_paths() -> None:
    assert ModuleReloader.file_to_module("app/main_page.py") == "app.main_page"
    assert ModuleReloader.file_to_module("app\\pages\\home.py") == "app.pages.home"
    assert ModuleReloader.file_to_module("app/__init__.py") == "app"


def test_reload_from_manifest_calls_reload_once(tmp_path: Path) -> None:
    writable_root = os.fspath(tmp_path)
    dev_root = configure_dev_environment(writable_root)
    manifest_path = manifest_path_for(dev_root)
    calls: list[list[str]] = []

    class Page:
        def reload(self, module_names: list[str]) -> None:
            calls.append(module_names)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": "1",
                "files": ["app/main_page.py"],
                "modules": ["app.main_page"],
            },
            f,
        )

    version = ModuleReloader.reload_from_manifest(Page(), manifest_path)
    assert version == "1"
    assert calls == [["app.main_page"]]

    version = ModuleReloader.reload_from_manifest(Page(), manifest_path, last_version=version)
    assert version == "1"
    assert calls == [["app.main_page"]]


def test_reload_module_imports_from_prioritized_sys_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundled = tmp_path / "bundled"
    overlay = tmp_path / "overlay"
    bundled_pkg = bundled / "reload_pkg"
    overlay_pkg = overlay / "reload_pkg"
    bundled_pkg.mkdir(parents=True)
    overlay_pkg.mkdir(parents=True)
    (bundled_pkg / "__init__.py").write_text("", encoding="utf-8")
    (overlay_pkg / "__init__.py").write_text("", encoding="utf-8")
    _write_module(bundled_pkg / "screen.py", "bundled")
    _write_module(overlay_pkg / "screen.py", "overlay")

    monkeypatch.syspath_prepend(os.fspath(bundled))
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    sys.modules.pop("reload_pkg.screen", None)
    sys.modules.pop("reload_pkg", None)

    screen = importlib.import_module("reload_pkg.screen")

    assert screen.VALUE == "bundled"

    monkeypatch.syspath_prepend(os.fspath(overlay))
    monkeypatch.setenv("PYTHONNATIVE_HOT_RELOAD_ROOT", os.fspath(overlay))
    assert ModuleReloader.reload_module("reload_pkg.screen") is True

    reloaded = importlib.import_module("reload_pkg.screen")

    assert reloaded.VALUE == "overlay"
