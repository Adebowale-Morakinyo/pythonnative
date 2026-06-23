"""Tests for the dev-client session state machine."""

import time
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

import pytest

import pythonnative.runtime as runtime_mod
import pythonnative.screen as screen_mod
from pythonnative.dev import session as session_mod
from pythonnative.dev.server import DevServer


def _wait_for(predicate: Callable[[], bool], timeout: float = 8.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return predicate()


class _DummyHost:
    def __init__(self) -> None:
        self._component_path: Optional[str] = None


def test_normalize_url_adds_scheme_and_trims() -> None:
    assert session_mod._normalize_url("192.168.1.5:8765") == "http://192.168.1.5:8765"
    assert session_mod._normalize_url("http://host:1/") == "http://host:1"
    assert session_mod._normalize_url("  ") == ""


def test_recent_servers_round_trip(tmp_path: Path) -> None:
    session = session_mod.DevSession(str(tmp_path / "overlay"))
    assert session.recent_servers() == []
    session._remember_server("http://a:1")
    session._remember_server("http://b:2")
    session._remember_server("http://a:1")  # moves to front, no dupes
    assert session.recent_servers() == ["http://a:1", "http://b:2"]


def test_scanner_registration() -> None:
    session = session_mod.DevSession("/tmp/does-not-matter")
    assert session.has_scanner() is False
    seen: List[str] = []
    session.set_scanner(lambda: seen.append("scan"))
    assert session.has_scanner() is True
    session.request_scan()
    assert seen == ["scan"]


@pytest.fixture()
def server(tmp_path: Path) -> Any:
    project = tmp_path / "project"
    (project / "app").mkdir(parents=True)
    (project / "app" / "main.py").write_text("App = 'x'\n", encoding="utf-8")
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


def test_connect_mounts_user_app_then_disconnect_returns_to_shell(
    server: DevServer,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mounts: List[Tuple[Any, str]] = []

    def fake_mount(host: Any, path: str, args_json: Optional[str] = None) -> None:
        host._component_path = path
        mounts.append((host, path))

    monkeypatch.setattr(screen_mod, "mount_component", fake_mount)
    # Run main-thread callbacks synchronously so assertions are deterministic.
    monkeypatch.setattr(runtime_mod, "call_on_main_thread", lambda fn: fn())

    host = _DummyHost()
    session = session_mod.DevSession(str(tmp_path / "overlay"))
    session.attach_host(host)

    url = f"http://127.0.0.1:{server.port}"
    session.connect(url)

    assert _wait_for(lambda: session.phase == session_mod.PHASE_CONNECTED)
    assert host._component_path == "app.main"
    assert session.entry_module == "app.main"
    assert session.app_name == "Demo"
    assert url in session.recent_servers()
    # The shell was shown while connecting, then the user app was mounted.
    mounted_paths = [path for _, path in mounts]
    assert screen_mod.DEV_CLIENT_ENTRY in mounted_paths
    assert mounted_paths[-1] == "app.main"

    session.disconnect()
    assert session.phase == session_mod.PHASE_IDLE
    assert host._component_path == screen_mod.DEV_CLIENT_ENTRY
    assert not (tmp_path / "overlay" / "app").exists()


def test_connect_reports_unreachable_server(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screen_mod, "mount_component", lambda *a, **k: None)
    monkeypatch.setattr(runtime_mod, "call_on_main_thread", lambda fn: fn())

    session = session_mod.DevSession(str(tmp_path / "overlay"))
    session.attach_host(_DummyHost())
    # Nothing is listening on this port.
    session.connect("http://127.0.0.1:1")

    assert _wait_for(lambda: session.phase == session_mod.PHASE_ERROR)
    assert "couldn't reach" in session.error.lower()
    session.disconnect()
