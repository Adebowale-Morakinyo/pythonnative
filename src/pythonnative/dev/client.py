"""Device-side dev client: download and live-sync an app bundle.

[`DevClient`][pythonnative.dev.client.DevClient] runs inside the PythonNative
Go app. It connects to a [`DevServer`][pythonnative.dev.server.DevServer],
downloads the project bundle into the on-device hot-reload overlay (the same
``pythonnative_dev/`` directory the existing Fast Refresh path already reads),
and then long-polls for changes, syncing only the files that differ.

Reloads ride the existing machinery: after syncing changed files the client
writes the overlay's ``reload.json`` manifest, which the screen host's
[`hot_reload_tick`][pythonnative.screen] already polls and applies as a
state-preserving Fast Refresh. That means the network loop reuses all of the
battle-tested on-device reload code instead of duplicating it.

Everything here is standard library (``urllib``, ``zipfile``) so it imports
cleanly under Chaquopy and the embedded iOS interpreter.
"""

from __future__ import annotations

import io
import json
import os
import zipfile
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.request import urlopen

from .protocol import (
    PATH_BUNDLE_ZIP,
    PATH_FILES_PREFIX,
    PATH_MANIFEST,
    PATH_POLL,
    PATH_STATUS,
    Manifest,
    PollResult,
    ServerStatus,
)

INSTALLED_MANIFEST = ".pn-bundle.json"
"""Filename, inside the overlay, recording the currently installed manifest."""

SITE_PACKAGES_DIR = "site-packages"
"""Overlay subdirectory for bundled pure-Python dependencies."""


@dataclass
class SyncResult:
    """Summary of an overlay sync.

    Attributes:
        changed_modules: Dotted module names under ``app`` that changed and
            should be Fast-Refreshed (e.g. ``["app.main"]``).
        written: Number of files written.
        removed: Number of files deleted from the overlay.
        version: The bundle version that is now installed.
    """

    changed_modules: List[str] = field(default_factory=list)
    written: int = 0
    removed: int = 0
    version: str = ""


def _module_for(bundle_path: str) -> Optional[str]:
    """Return the dotted module name for an ``app/...`` bundle path, else ``None``."""
    if not bundle_path.endswith(".py"):
        return None
    if not (bundle_path == "app" or bundle_path.startswith("app/")):
        return None
    trimmed = bundle_path[:-3]
    parts = trimmed.split("/")
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else None


class DevClient:
    """HTTP client for one dev-server connection and its overlay.

    Args:
        base_url: The dev-server base URL (``http://host:port``, no trailing
            slash).
        overlay_root: The on-device hot-reload overlay directory (from
            [`configure_dev_environment`][pythonnative.hot_reload.configure_dev_environment]).
        timeout: Default request timeout in seconds for non-poll requests.
    """

    def __init__(self, base_url: str, overlay_root: str, *, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.overlay_root = overlay_root
        self.timeout = timeout

    # -- raw HTTP -------------------------------------------------------

    def _get(self, path: str, *, timeout: Optional[float] = None) -> bytes:
        url = self.base_url + path
        with urlopen(url, timeout=timeout if timeout is not None else self.timeout) as response:
            return bytes(response.read())

    def fetch_status(self) -> ServerStatus:
        """Fetch the server handshake (``/status``)."""
        return ServerStatus.from_json(self._get(PATH_STATUS).decode("utf-8"))

    def fetch_manifest(self) -> Manifest:
        """Fetch the current bundle manifest (``/manifest.json``)."""
        return Manifest.from_json(self._get(PATH_MANIFEST).decode("utf-8"))

    def poll(self, since: str, *, timeout: float = 35.0) -> PollResult:
        """Long-poll for a bundle version newer than ``since`` (``/poll``)."""
        return PollResult.from_json(self._get(f"{PATH_POLL}?since={since}", timeout=timeout).decode("utf-8"))

    # -- overlay state --------------------------------------------------

    def _overlay_path(self, bundle_path: str) -> str:
        return os.path.join(self.overlay_root, *bundle_path.split("/"))

    def installed_manifest(self) -> Optional[Manifest]:
        """Return the manifest currently installed in the overlay, if any."""
        path = os.path.join(self.overlay_root, INSTALLED_MANIFEST)
        if not os.path.exists(path):
            return None
        try:
            with open(path, encoding="utf-8") as handle:
                return Manifest.from_json(handle.read())
        except (OSError, ValueError):
            return None

    def _save_installed_manifest(self, manifest: Manifest) -> None:
        os.makedirs(self.overlay_root, exist_ok=True)
        path = os.path.join(self.overlay_root, INSTALLED_MANIFEST)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(manifest.to_json())

    def _write_file(self, bundle_path: str, data: bytes) -> None:
        target = self._overlay_path(bundle_path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as handle:
            handle.write(data)

    def _remove_file(self, bundle_path: str) -> None:
        target = self._overlay_path(bundle_path)
        try:
            os.remove(target)
        except OSError:
            pass

    # -- install / sync -------------------------------------------------

    def install(self) -> SyncResult:
        """Download the full bundle (zip) into the overlay.

        Used for the first connection, when nothing is installed yet. Writes
        every file and records the installed manifest.

        Returns:
            A [`SyncResult`][pythonnative.dev.client.SyncResult] for the install.
        """
        manifest = self.fetch_manifest()
        data = self._get(PATH_BUNDLE_ZIP)
        os.makedirs(self.overlay_root, exist_ok=True)
        written = 0
        modules: List[str] = []
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for name in archive.namelist():
                if name.endswith("/"):
                    continue
                self._write_file(name, archive.read(name))
                written += 1
                module = _module_for(name)
                if module:
                    modules.append(module)
        self._save_installed_manifest(manifest)
        self._ensure_site_packages_on_path()
        return SyncResult(changed_modules=modules, written=written, removed=0, version=manifest.version)

    def sync(self) -> SyncResult:
        """Sync the overlay to the latest manifest, fetching only differences.

        Downloads files whose hash changed or that are new, deletes files
        that disappeared, and records the new installed manifest.

        Returns:
            A [`SyncResult`][pythonnative.dev.client.SyncResult] listing the
            changed ``app`` modules so the caller can trigger Fast Refresh.
        """
        previous = self.installed_manifest()
        if previous is None:
            return self.install()

        manifest = self.fetch_manifest()
        old = previous.by_path()
        new = manifest.by_path()

        written = 0
        removed = 0
        modules: List[str] = []
        for path, entry in new.items():
            if path in old and old[path].sha256 == entry.sha256:
                continue
            data = self._get(PATH_FILES_PREFIX + path)
            self._write_file(path, data)
            written += 1
            module = _module_for(path)
            if module:
                modules.append(module)
        for path in old:
            if path not in new:
                self._remove_file(path)
                removed += 1
                module = _module_for(path)
                if module:
                    modules.append(module)

        self._save_installed_manifest(manifest)
        self._ensure_site_packages_on_path()
        return SyncResult(changed_modules=modules, written=written, removed=removed, version=manifest.version)

    def _ensure_site_packages_on_path(self) -> None:
        """Add the overlay's ``site-packages`` to ``sys.path`` when present."""
        import sys

        site = os.path.join(self.overlay_root, SITE_PACKAGES_DIR)
        if os.path.isdir(site) and site not in sys.path:
            sys.path.insert(0, site)

    def write_reload_manifest(self, modules: List[str], version: str) -> None:
        """Write the overlay ``reload.json`` so the screen host Fast-Refreshes.

        This reuses the existing on-device reload path: the screen host's
        ``hot_reload_tick`` polls this manifest and applies a
        state-preserving refresh of the changed modules.

        Args:
            modules: Dotted module names that changed.
            version: A unique version token for this reload.
        """
        from ..hot_reload import manifest_path_for

        payload = {"version": version, "modules": modules, "files": []}
        path = manifest_path_for(self.overlay_root)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)


def clear_overlay(overlay_root: str) -> None:
    """Delete a previously installed bundle from the overlay.

    Used when disconnecting or switching servers so a fresh connection
    starts from a clean slate.

    Args:
        overlay_root: The hot-reload overlay directory.
    """
    import shutil

    for name in ("app", SITE_PACKAGES_DIR, INSTALLED_MANIFEST, "reload.json"):
        target = os.path.join(overlay_root, name)
        if os.path.isdir(target):
            shutil.rmtree(target, ignore_errors=True)
        elif os.path.exists(target):
            try:
                os.remove(target)
            except OSError:
                pass
