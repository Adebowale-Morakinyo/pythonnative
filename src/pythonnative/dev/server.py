"""The PythonNative dev server behind ``pn start``.

[`DevServer`][pythonnative.dev.server.DevServer] is a small threaded HTTP
server that serves a project [`Bundle`][pythonnative.dev.bundle.Bundle] to the
PythonNative Go app and pushes live updates: it watches the project's ``app/``
directory and, on every save, rebuilds the bundle and bumps a version token
that long-polling clients are waiting on. The result is the Expo-style inner
loop: edit a ``.py`` file, the phone refreshes in well under a second, with no
native rebuild.

The protocol lives in [`pythonnative.dev.protocol`][pythonnative.dev.protocol];
this module is the host-side implementation of it. It is pure standard library
(``http.server`` + threads) so ``pn start`` needs no extra dependencies.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import parse_qs, urlparse

from ..hot_reload import FileWatcher
from .bundle import APP_DIR, Bundle, build_bundle, new_version
from .protocol import (
    PATH_BUNDLE_ZIP,
    PATH_FILES_PREFIX,
    PATH_MANIFEST,
    PATH_POLL,
    PATH_ROOT,
    PATH_STATUS,
    POLL_TIMEOUT_SECONDS,
    PROTOCOL_VERSION,
    SERVER_NAME,
    Manifest,
    PollResult,
    ServerStatus,
)

Logger = Callable[[str], None]


def _sdk_version() -> str:
    try:
        from .. import __version__

        return str(__version__)
    except Exception:
        return "unknown"


class DevServer:
    """Serve a project bundle with live reload over HTTP.

    Args:
        project_root: Directory containing ``app/`` and ``pythonnative.toml``.
        app_name: Project name shown in the client connect UI.
        entry_module: Dotted entry module the client mounts (e.g. ``"app.main"``).
        host: Interface to bind (``"0.0.0.0"`` to accept LAN connections).
        port: TCP port to listen on.
        site_packages: Optional directory of pure-Python dependencies to
            include in the bundle.
        watch: Whether to watch ``app/`` and push updates on change.
        log: Progress logger (defaults to a no-op).
    """

    def __init__(
        self,
        project_root: Path,
        *,
        app_name: str,
        entry_module: str,
        host: str = "0.0.0.0",
        port: int = 0,
        site_packages: Optional[Path] = None,
        watch: bool = True,
        log: Optional[Logger] = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.app_name = app_name
        self.entry_module = entry_module
        self.host = host
        self._site_packages = site_packages
        self._watch = watch
        self.log: Logger = log or (lambda _msg: None)

        self._lock = threading.Condition()
        self._bundle: Bundle = self._build_bundle(new_version())
        self._manifest: Manifest = self._bundle.manifest()

        self._httpd = ThreadingHTTPServer((host, port), _Handler)
        # Expose this DevServer to request handlers via the HTTPServer.
        self._httpd.dev_server = self
        self.port = self._httpd.server_address[1]

        self._watcher: Optional[FileWatcher] = None
        self._serve_thread: Optional[threading.Thread] = None

    # -- bundle management ---------------------------------------------

    def _build_bundle(self, version: str) -> Bundle:
        return build_bundle(
            self.project_root,
            app_name=self.app_name,
            entry_module=self.entry_module,
            sdk_version=_sdk_version(),
            site_packages=self._site_packages,
            version=version,
        )

    def rebuild(self) -> str:
        """Rebuild the bundle and bump the version, waking pollers.

        Called by the file watcher on every change. Returns the new
        version token.

        Returns:
            The new bundle version.
        """
        version = new_version()
        bundle = self._build_bundle(version)
        manifest = bundle.manifest()
        with self._lock:
            self._bundle = bundle
            self._manifest = manifest
            self._lock.notify_all()
        return version

    def manifest(self) -> Manifest:
        """Return the current bundle manifest (thread-safe)."""
        with self._lock:
            return self._manifest

    def status(self) -> ServerStatus:
        """Return the ``/status`` handshake payload for the current bundle."""
        with self._lock:
            manifest = self._manifest
        return ServerStatus(
            server=SERVER_NAME,
            protocol_version=PROTOCOL_VERSION,
            sdk_version=manifest.sdk_version,
            app_name=manifest.app_name,
            entry_module=manifest.entry_module,
            version=manifest.version,
        )

    def read_file(self, bundle_path: str) -> Optional[bytes]:
        """Return the bytes of one bundled file, or ``None`` if not present.

        Args:
            bundle_path: A POSIX bundle path (e.g. ``"app/main.py"``).

        Returns:
            The file contents, or ``None`` when the path isn't part of the
            current bundle (which also blocks path traversal).
        """
        with self._lock:
            bundle = self._bundle
        if bundle_path not in bundle.files:
            return None
        try:
            return bundle.read(bundle_path)
        except (KeyError, OSError):
            return None

    def zip_bytes(self) -> bytes:
        """Return the current bundle as a zip archive (thread-safe)."""
        with self._lock:
            bundle = self._bundle
        return bundle.zip_bytes()

    def wait_for_change(self, since: str, timeout: float = POLL_TIMEOUT_SECONDS) -> PollResult:
        """Block until the bundle version differs from ``since`` or ``timeout``.

        Args:
            since: The version token the client currently has.
            timeout: Maximum seconds to wait before returning unchanged.

        Returns:
            A [`PollResult`][pythonnative.dev.protocol.PollResult] whose
            ``changed`` flag indicates whether the version advanced.
        """
        deadline_check = since
        with self._lock:
            if self._manifest.version != deadline_check:
                return PollResult(version=self._manifest.version, changed=True)
            self._lock.wait(timeout)
            version = self._manifest.version
        return PollResult(version=version, changed=version != deadline_check)

    # -- lifecycle ------------------------------------------------------

    def start(self) -> None:
        """Start serving and watching in background threads (non-blocking)."""
        if self._watch:
            self._watcher = FileWatcher(str(self.project_root / APP_DIR), self._on_change, interval=0.4)
            self._watcher.start()
        self._serve_thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._serve_thread.start()

    def serve_forever(self) -> None:
        """Start (if needed) and block until [`stop`][pythonnative.dev.server.DevServer.stop].

        Suitable for the ``pn start`` foreground command; handles
        ``KeyboardInterrupt`` by stopping cleanly.
        """
        if self._watch and self._watcher is None:
            self._watcher = FileWatcher(str(self.project_root / APP_DIR), self._on_change, interval=0.4)
            self._watcher.start()
        try:
            self._httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the HTTP server and file watcher and release the socket."""
        if self._watcher is not None:
            try:
                self._watcher.stop()
            except Exception:
                pass
            self._watcher = None
        try:
            self._httpd.shutdown()
        except Exception:
            pass
        try:
            self._httpd.server_close()
        except Exception:
            pass

    def _on_change(self, changed_files: Any) -> None:
        version = self.rebuild()
        names = ", ".join(sorted(Path(f).name for f in changed_files)) or "files"
        self.log(f"[pn start] changed: {names} -> reloading (v{version})")


class _Handler(BaseHTTPRequestHandler):
    """HTTP request handler bound to a [`DevServer`][pythonnative.dev.server.DevServer]."""

    protocol_version = "HTTP/1.1"

    @property
    def _dev(self) -> DevServer:
        return self.server.dev_server

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - signature fixed by stdlib
        """Silence the default per-request stderr logging."""
        return

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_json(self, payload: Any, status: int = 200) -> None:
        self._send(status, json.dumps(payload).encode("utf-8"), "application/json")

    def do_GET(self) -> None:  # noqa: N802 - stdlib-mandated name
        """Route a GET request to the matching dev-server endpoint."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == PATH_ROOT:
            self._send(200, self._index_html(), "text/html; charset=utf-8")
            return
        if path == PATH_STATUS:
            self._send_json(self._dev.status().to_dict())
            return
        if path == PATH_MANIFEST:
            self._send_json(self._dev.manifest().to_dict())
            return
        if path == PATH_BUNDLE_ZIP:
            self._send(200, self._dev.zip_bytes(), "application/zip")
            return
        if path == PATH_POLL:
            params = parse_qs(parsed.query)
            since = (params.get("since") or [""])[0]
            result = self._dev.wait_for_change(since)
            self._send_json(result.to_dict())
            return
        if path.startswith(PATH_FILES_PREFIX):
            bundle_path = path[len(PATH_FILES_PREFIX) :]
            data = self._dev.read_file(bundle_path)
            if data is None:
                self._send_json({"error": "not found", "path": bundle_path}, status=404)
                return
            self._send(200, data, "application/octet-stream")
            return

        self._send_json({"error": "not found", "path": path}, status=404)

    def _index_html(self) -> bytes:
        status = self._dev.status()
        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>PythonNative dev server</title>"
            "<style>body{font-family:-apple-system,system-ui,sans-serif;max-width:40rem;"
            "margin:3rem auto;padding:0 1rem;color:#1c1c1e}code{background:#f2f2f7;"
            "padding:.1rem .35rem;border-radius:.25rem}</style></head><body>"
            "<h1>PythonNative dev server</h1>"
            f"<p>Serving <strong>{status.app_name}</strong> "
            f"(entry <code>{status.entry_module}</code>, SDK {status.sdk_version}).</p>"
            "<p>Open <strong>PythonNative Go</strong> on your device and scan the QR "
            "code shown in the terminal, or enter this URL manually.</p>"
            f"<p>Bundle version <code>{status.version}</code>.</p>"
            "</body></html>"
        ).encode("utf-8")
