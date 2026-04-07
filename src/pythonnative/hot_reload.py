"""Hot-reload support for PythonNative development.

Host-side
~~~~~~~~~
:class:`FileWatcher` monitors the ``app/`` directory for changes and
triggers a push-and-reload cycle via ``adb push`` (Android) or
``simctl`` file copy (iOS).

Device-side
~~~~~~~~~~~
:class:`ModuleReloader` reloads changed Python modules using
``importlib.reload`` and triggers a page re-render.

Usage (host-side, integrated into ``pn run --hot-reload``)::

    watcher = FileWatcher("app/", on_change=push_files)
    watcher.start()
"""

import importlib
import os
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional

# ======================================================================
# Host-side file watcher
# ======================================================================


class FileWatcher:
    """Watch a directory tree for ``.py`` file changes.

    Parameters
    ----------
    watch_dir:
        Directory to watch.
    on_change:
        Called with a list of changed file paths when modifications are detected.
    interval:
        Polling interval in seconds.
    """

    def __init__(self, watch_dir: str, on_change: Callable[[List[str]], None], interval: float = 1.0) -> None:
        self.watch_dir = watch_dir
        self.on_change = on_change
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._mtimes: Dict[str, float] = {}

    def start(self) -> None:
        """Begin watching in a background daemon thread."""
        self._running = True
        self._scan()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the watcher."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=self.interval * 2)
            self._thread = None

    def _scan(self) -> List[str]:
        changed: List[str] = []
        current_files: set = set()

        for root, _dirs, files in os.walk(self.watch_dir):
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                fpath = os.path.join(root, fname)
                current_files.add(fpath)
                try:
                    mtime = os.path.getmtime(fpath)
                except OSError:
                    continue
                if fpath in self._mtimes:
                    if mtime > self._mtimes[fpath]:
                        changed.append(fpath)
                self._mtimes[fpath] = mtime

        for old in list(self._mtimes):
            if old not in current_files:
                del self._mtimes[old]

        return changed

    def _loop(self) -> None:
        while self._running:
            time.sleep(self.interval)
            changed = self._scan()
            if changed:
                try:
                    self.on_change(changed)
                except Exception:
                    pass


# ======================================================================
# Device-side module reloader
# ======================================================================


class ModuleReloader:
    """Reload changed Python modules on device and trigger re-render."""

    @staticmethod
    def reload_module(module_name: str) -> bool:
        """Reload a single module by its dotted name.

        Returns ``True`` if the module was found and reloaded successfully.
        """
        mod = sys.modules.get(module_name)
        if mod is None:
            return False
        try:
            importlib.reload(mod)
            return True
        except Exception:
            return False

    @staticmethod
    def file_to_module(file_path: str, base_dir: str = "") -> Optional[str]:
        """Convert a file path to a dotted module name relative to *base_dir*."""
        rel = os.path.relpath(file_path, base_dir) if base_dir else file_path
        if rel.endswith(".py"):
            rel = rel[:-3]
        parts = rel.replace(os.sep, ".").split(".")
        if parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts) if parts else None

    @staticmethod
    def reload_page(page_instance: Any) -> None:
        """Force a page re-render after module reload."""
        from .page import _request_render

        if hasattr(page_instance, "_reconciler") and page_instance._reconciler is not None:
            _request_render(page_instance)
