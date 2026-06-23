"""Integration tests for the dev server and dev client over localhost."""

import json
from pathlib import Path
from typing import Iterator

import pytest

from pythonnative.dev.client import DevClient, clear_overlay
from pythonnative.dev.server import DevServer


def _make_project(root: Path, body: str = "App = 'before'\n") -> None:
    app = root / "app"
    app.mkdir(exist_ok=True)
    (app / "main.py").write_text(body, encoding="utf-8")


@pytest.fixture()
def server(tmp_path: Path) -> Iterator[DevServer]:
    project = tmp_path / "project"
    project.mkdir()
    _make_project(project)
    srv = DevServer(
        project,
        app_name="Demo",
        entry_module="app.main",
        host="127.0.0.1",
        port=0,
        watch=False,
    )
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


def test_status_handshake(server: DevServer, tmp_path: Path) -> None:
    client = DevClient(f"http://127.0.0.1:{server.port}", str(tmp_path / "overlay"))
    status = client.fetch_status()
    assert status.is_pythonnative()
    assert status.app_name == "Demo"
    assert status.entry_module == "app.main"


def test_install_writes_overlay_and_manifest(server: DevServer, tmp_path: Path) -> None:
    overlay = tmp_path / "overlay"
    client = DevClient(f"http://127.0.0.1:{server.port}", str(overlay))
    result = client.install()

    assert (overlay / "app" / "main.py").read_text(encoding="utf-8") == "App = 'before'\n"
    assert result.written == 1
    assert "app.main" in result.changed_modules
    # Installed manifest is recorded so a later sync only fetches diffs.
    saved = client.installed_manifest()
    assert saved is not None
    assert saved.by_path()["app/main.py"].size == len("App = 'before'\n")


def test_poll_detects_change_and_sync_fetches_diff(server: DevServer, tmp_path: Path) -> None:
    overlay = tmp_path / "overlay"
    base = f"http://127.0.0.1:{server.port}"
    client = DevClient(base, str(overlay))

    install = client.install()
    version = install.version

    # Developer edits a file; the server rebuilds and bumps the version.
    _make_project(server.project_root, body="App = 'after'\n")
    new_version = server.rebuild()
    assert new_version != version

    # A poll with a stale version returns immediately with the new one.
    changed = client.poll(version, timeout=5.0)
    assert changed.changed is True
    assert changed.version == new_version

    sync = client.sync()
    assert sync.version == new_version
    assert "app.main" in sync.changed_modules
    assert (overlay / "app" / "main.py").read_text(encoding="utf-8") == "App = 'after'\n"


def test_wait_for_change_returns_unchanged_after_timeout(server: DevServer) -> None:
    version = server.manifest().version
    # Long-poll the server directly with a tiny timeout so the test stays fast.
    result = server.wait_for_change(version, timeout=0.1)
    assert result.changed is False
    assert result.version == version


def test_sync_removes_deleted_files(server: DevServer, tmp_path: Path) -> None:
    overlay = tmp_path / "overlay"
    client = DevClient(f"http://127.0.0.1:{server.port}", str(overlay))

    # Add a second file, install, then delete it and re-sync.
    (server.project_root / "app" / "extra.py").write_text("X = 1\n", encoding="utf-8")
    server.rebuild()
    client.install()
    assert (overlay / "app" / "extra.py").exists()

    (server.project_root / "app" / "extra.py").unlink()
    server.rebuild()
    sync = client.sync()
    assert sync.removed == 1
    assert not (overlay / "app" / "extra.py").exists()


def test_write_reload_manifest_matches_overlay(server: DevServer, tmp_path: Path) -> None:
    overlay = tmp_path / "overlay"
    client = DevClient(f"http://127.0.0.1:{server.port}", str(overlay))
    client.install()
    client.write_reload_manifest(["app.main"], "v123")
    payload = json.loads((overlay / "reload.json").read_text(encoding="utf-8"))
    assert payload["version"] == "v123"
    assert payload["modules"] == ["app.main"]


def test_clear_overlay_removes_installed_bundle(server: DevServer, tmp_path: Path) -> None:
    overlay = tmp_path / "overlay"
    client = DevClient(f"http://127.0.0.1:{server.port}", str(overlay))
    client.install()
    assert (overlay / "app" / "main.py").exists()
    clear_overlay(str(overlay))
    assert not (overlay / "app").exists()
    assert client.installed_manifest() is None
