"""Dev-client session: connection state machine for PythonNative Go.

A single process-wide [`DevSession`][pythonnative.dev.session.DevSession] owns
the connection to a dev server and drives what the screen host shows:

- **idle** -> the connect screen (enter or scan a server URL).
- **connecting** -> a loading screen while the bundle downloads.
- **connected** -> the host is re-pointed to the *user's* entry module, so the
  app runs (and Fast-Refreshes) exactly as it would in a normal build.
- **error** -> a red error screen with the failure, plus retry/disconnect.

The shell UI ([`pythonnative.dev.ui`][pythonnative.dev.ui]) reads this session
and subscribes for changes; the native dev menu (shake gesture) calls
[`reload`][pythonnative.dev.session.reload] /
[`disconnect`][pythonnative.dev.session.disconnect]. Network work runs on a
background thread; anything that touches the reconciler is marshaled to the UI
thread via [`runtime.call_on_main_thread`][pythonnative.runtime.call_on_main_thread].
"""

from __future__ import annotations

import json
import os
import threading
import time
import traceback
from typing import Callable, List, Optional

from .client import DevClient, clear_overlay
from .protocol import is_compatible

PHASE_IDLE = "idle"
PHASE_CONNECTING = "connecting"
PHASE_CONNECTED = "connected"
PHASE_ERROR = "error"

RECENT_SERVERS_FILE = ".pn-servers.json"
_MAX_RECENT = 6


def _local_sdk_version() -> str:
    try:
        from .. import __version__

        return str(__version__)
    except Exception:
        return ""


class DevSession:
    """Owns one dev-server connection and the screen host it drives.

    Args:
        overlay_root: The on-device hot-reload overlay directory that bundles
            are installed into.
    """

    def __init__(self, overlay_root: str) -> None:
        self.overlay_root = overlay_root
        self.phase = PHASE_IDLE
        self.base_url = ""
        self.app_name = ""
        self.entry_module = "app.main"
        self.error = ""
        self.warning = ""

        self._client: Optional[DevClient] = None
        self._version = ""
        self._host: object = None
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._subscribers: List[Callable[[], None]] = []
        self._scanner: Optional[Callable[[], None]] = None
        self.log: Callable[[str], None] = lambda _msg: None

    # -- UI subscription ------------------------------------------------

    def subscribe(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Register ``callback`` to run (on the UI thread) on every change.

        Args:
            callback: Invoked after any phase/field change so a subscribed
                component can re-render.

        Returns:
            An unsubscribe function.
        """
        self._subscribers.append(callback)

        def _unsubscribe() -> None:
            try:
                self._subscribers.remove(callback)
            except ValueError:
                pass

        return _unsubscribe

    def _emit(self) -> None:
        for callback in list(self._subscribers):
            try:
                callback()
            except Exception:
                pass

    # -- host binding ---------------------------------------------------

    def attach_host(self, host: object) -> None:
        """Bind the screen host this session re-points between shell and app."""
        self._host = host

    # -- native QR scanner ----------------------------------------------

    def set_scanner(self, scanner: Optional[Callable[[], None]]) -> None:
        """Register the native QR scanner used by the connect screen's button."""
        self._scanner = scanner

    def has_scanner(self) -> bool:
        """Return whether a native QR scanner is available on this platform."""
        return self._scanner is not None

    def request_scan(self) -> None:
        """Ask the native layer to open the QR scanner (no-op if unavailable)."""
        if self._scanner is not None:
            try:
                self._scanner()
            except Exception:
                pass

    # -- recent servers -------------------------------------------------

    def recent_servers(self) -> List[str]:
        """Return recently used server URLs, most recent first."""
        path = os.path.join(self.overlay_root, RECENT_SERVERS_FILE)
        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, list):
                return [str(item) for item in data][:_MAX_RECENT]
        except (OSError, ValueError):
            pass
        return []

    def _remember_server(self, url: str) -> None:
        servers = [url] + [s for s in self.recent_servers() if s != url]
        servers = servers[:_MAX_RECENT]
        os.makedirs(self.overlay_root, exist_ok=True)
        path = os.path.join(self.overlay_root, RECENT_SERVERS_FILE)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(servers, handle)
        except OSError:
            pass

    # -- main-thread marshaling -----------------------------------------

    def _on_main(self, fn: Callable[[], None]) -> None:
        try:
            from .. import runtime

            runtime.call_on_main_thread(fn)
        except Exception:
            fn()

    def _transition(self, phase: str, **fields: str) -> None:
        self.phase = phase
        for key, value in fields.items():
            setattr(self, key, value)
        self._on_main(self._apply)

    def _apply(self) -> None:
        """Reconcile the screen host with the current phase (UI thread)."""
        if self.phase == PHASE_CONNECTED:
            self._mount_user_app()
        else:
            self._mount_shell()
        self._emit()

    def _mount_user_app(self) -> None:
        host = self._host
        if host is None:
            return
        try:
            from .. import screen

            if getattr(host, "_component_path", None) != self.entry_module:
                screen.mount_component(host, self.entry_module)
        except Exception:
            self.phase = PHASE_ERROR
            self.error = traceback.format_exc()
            self._mount_shell()

    def _mount_shell(self) -> None:
        host = self._host
        if host is None:
            return
        try:
            from .. import screen

            if getattr(host, "_component_path", None) != screen.DEV_CLIENT_ENTRY:
                screen.mount_component(host, screen.DEV_CLIENT_ENTRY)
        except Exception:
            pass

    # -- lifecycle ------------------------------------------------------

    def connect(self, url: str) -> None:
        """Connect to a dev server and mount its app (runs in the background).

        Args:
            url: The dev-server base URL, e.g. ``http://192.168.1.20:8765``.
        """
        url = _normalize_url(url)
        if not url:
            self._transition(PHASE_ERROR, error="Enter a server URL like http://192.168.1.20:8765")
            return
        self._stop_thread()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, args=(url,), daemon=True)
        self._thread.start()

    def _run(self, url: str) -> None:
        self._transition(PHASE_CONNECTING, base_url=url, error="", warning="")
        client = DevClient(url, self.overlay_root)
        try:
            status = client.fetch_status()
        except Exception as exc:
            self._transition(PHASE_ERROR, error=f"Couldn't reach the dev server at {url}.\n\n{exc}")
            return
        if not status.is_pythonnative():
            self._transition(PHASE_ERROR, error=f"{url} doesn't look like a PythonNative dev server.")
            return
        if not is_compatible(status.protocol_version):
            self._transition(
                PHASE_ERROR,
                error="Protocol mismatch. Update PythonNative Go or your `pn` CLI so they match.",
            )
            return

        warning = ""
        local = _local_sdk_version()
        if status.sdk_version and local and status.sdk_version != local:
            warning = f"SDK mismatch: server is {status.sdk_version}, this app bundles {local}."

        clear_overlay(self.overlay_root)
        try:
            result = client.install()
        except Exception as exc:
            self._transition(PHASE_ERROR, error=f"Failed to download the app bundle.\n\n{exc}")
            return

        self._client = client
        self._version = result.version
        self.entry_module = status.entry_module
        self.app_name = status.app_name
        self._remember_server(url)
        self.log(f"[pn] connected to {url} ({status.app_name})")
        self._transition(PHASE_CONNECTED, warning=warning)
        self._poll_loop(client)

    def _poll_loop(self, client: DevClient) -> None:
        while not self._stop.is_set():
            try:
                result = client.poll(self._version, timeout=35.0)
            except Exception:
                if self._stop.wait(1.0):
                    break
                continue
            if self._stop.is_set():
                break
            if not result.changed:
                continue
            try:
                sync = client.sync()
                self._version = sync.version
                if sync.changed_modules:
                    client.write_reload_manifest(sync.changed_modules, str(time.time_ns()))
                    self.log(f"[pn] reloaded: {', '.join(sync.changed_modules)}")
            except Exception:
                if self._stop.wait(0.5):
                    break

    def reload(self) -> None:
        """Force a full remount of the connected app (the dev-menu "Reload")."""
        if self.phase != PHASE_CONNECTED:
            return

        def _force() -> None:
            host = self._host
            if host is None:
                return
            try:
                from .. import screen

                screen.mount_component(host, self.entry_module)
            except Exception:
                self._transition(PHASE_ERROR, error=traceback.format_exc())

        self._on_main(_force)

    def disconnect(self) -> None:
        """Disconnect, clear the overlay, and return to the connect screen."""
        self._stop_thread()
        self._client = None
        clear_overlay(self.overlay_root)
        self._transition(PHASE_IDLE, error="", warning="")

    def _stop_thread(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=1.0)
        self._thread = None


def _normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if "://" not in url:
        url = "http://" + url
    return url.rstrip("/")


_SESSION: Optional[DevSession] = None


def get_session() -> DevSession:
    """Return the process-wide [`DevSession`][pythonnative.dev.session.DevSession].

    The overlay root is read from ``PYTHONNATIVE_HOT_RELOAD_ROOT`` (set by
    [`configure_dev_environment`][pythonnative.hot_reload.configure_dev_environment]),
    falling back to ``pythonnative_dev`` under the working directory.

    Returns:
        The singleton session, created on first use.
    """
    global _SESSION
    if _SESSION is None:
        root = os.environ.get("PYTHONNATIVE_HOT_RELOAD_ROOT") or os.path.join(os.getcwd(), "pythonnative_dev")
        _SESSION = DevSession(root)
    return _SESSION


def reset_session() -> None:
    """Drop the singleton session (used by tests)."""
    global _SESSION
    if _SESSION is not None:
        _SESSION._stop_thread()
    _SESSION = None


def connect(url: str) -> None:
    """Connect the global session to ``url`` (callable from native code)."""
    get_session().connect(url)


def disconnect() -> None:
    """Disconnect the global session (callable from the native dev menu)."""
    get_session().disconnect()


def reload() -> None:
    """Reload the connected app (callable from the native dev menu)."""
    get_session().reload()


def set_scanner(scanner: Optional[Callable[[], None]]) -> None:
    """Register the native QR scanner with the global session."""
    get_session().set_scanner(scanner)
