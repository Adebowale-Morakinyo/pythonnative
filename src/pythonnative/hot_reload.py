"""Hot-reload support for PythonNative development.

Two cooperating pieces:

- **Host-side**: [`FileWatcher`][pythonnative.hot_reload.FileWatcher]
  polls the developer's `app/` directory for `.py` changes and
  triggers a callback (typically `adb push` on Android or a
  `simctl` file copy on iOS).
- **Device-side**:
  [`ModuleReloader`][pythonnative.hot_reload.ModuleReloader] reloads
  changed Python modules using `importlib.reload` and asks the page
  host to re-render the current tree.

Example:
    Integrated into `pn run --hot-reload`:

    ```python
    from pythonnative.hot_reload import FileWatcher

    def push(changed):
        for path in changed:
            print("changed:", path)

    watcher = FileWatcher("app/", on_change=push)
    watcher.start()
    ```
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
    """Watch a directory tree for `.py` file changes.

    Uses simple `os.path.getmtime` polling rather than a native
    inotify/FSEvents binding so the watcher works on every platform
    where Python runs without extra dependencies.

    Args:
        watch_dir: Directory to watch (recursively).
        on_change: Called with a list of changed file paths when
            modifications are detected.
        interval: Polling interval, in seconds.

    Attributes:
        watch_dir: Directory being watched.
        on_change: Change callback.
        interval: Polling interval.
    """

    def __init__(self, watch_dir: str, on_change: Callable[[List[str]], None], interval: float = 1.0) -> None:
        self.watch_dir = watch_dir
        self.on_change = on_change
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._mtimes: Dict[str, float] = {}

    def start(self) -> None:
        """Begin watching in a background daemon thread.

        Performs an initial scan to seed mtimes so the first
        notification reflects subsequent edits, not pre-existing files.
        """
        self._running = True
        self._scan()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the watcher and join the background thread."""
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
    """Reload changed Python modules on device and trigger a re-render.

    Designed to be invoked from device-side glue when a hot-reload
    push completes. The class itself holds no state; all methods are
    static.
    """

    @staticmethod
    def reload_module(module_name: str) -> bool:
        """Reload a single module by its dotted name.

        Args:
            module_name: Dotted module name (e.g., `"app.main_page"`).

        Returns:
            `True` if the module was found in `sys.modules` and
            reloaded without raising; `False` otherwise.
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
        """Convert a file path to a dotted module name.

        Args:
            file_path: Path to a `.py` file (absolute or relative).
            base_dir: Base directory that names should be relative to.
                If empty, `file_path` is treated as already relative.

        Returns:
            The dotted module name (e.g., `"app.pages.home"`), or
            `None` for an empty path.
        """
        rel = os.path.relpath(file_path, base_dir) if base_dir else file_path
        if rel.endswith(".py"):
            rel = rel[:-3]
        parts = rel.replace(os.sep, ".").split(".")
        if parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts) if parts else None

    @staticmethod
    def reload_page(page_instance: Any) -> None:
        """Force a page re-render after a module reload.

        Args:
            page_instance: An `_AppHost` instance (or duck-typed
                equivalent) that exposes a `_reconciler` attribute.
        """
        from .page import _request_render

        if hasattr(page_instance, "_reconciler") and page_instance._reconciler is not None:
            _request_render(page_instance)
