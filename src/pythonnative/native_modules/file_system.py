"""Cross-platform file system access.

Provides helpers for reading and writing files within the app's
sandboxed storage area.
"""

import os
from typing import Any, Optional

from ..utils import IS_ANDROID


class FileSystem:
    """App-scoped file I/O."""

    @staticmethod
    def app_dir() -> str:
        """Return the app's writable data directory."""
        if IS_ANDROID:
            try:
                from ..utils import get_android_context

                return str(get_android_context().getFilesDir().getAbsolutePath())
            except Exception:
                pass
        else:
            try:
                from rubicon.objc import ObjCClass

                NSSearchPathForDirectoriesInDomains = ObjCClass(
                    "NSFileManager"
                ).defaultManager.URLsForDirectory_inDomains_
                docs = NSSearchPathForDirectoriesInDomains(9, 1)  # NSDocumentDirectory, NSUserDomainMask
                if docs and docs.count > 0:
                    return str(docs.objectAtIndex_(0).path)
            except Exception:
                pass
        return os.path.join(os.path.expanduser("~"), ".pythonnative_data")

    @staticmethod
    def read_text(path: str, encoding: str = "utf-8") -> Optional[str]:
        """Read a text file relative to :meth:`app_dir` (or an absolute path)."""
        full = path if os.path.isabs(path) else os.path.join(FileSystem.app_dir(), path)
        try:
            with open(full, encoding=encoding) as f:
                return f.read()
        except OSError:
            return None

    @staticmethod
    def write_text(path: str, content: str, encoding: str = "utf-8") -> bool:
        """Write a text file. Returns ``True`` on success."""
        full = path if os.path.isabs(path) else os.path.join(FileSystem.app_dir(), path)
        try:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding=encoding) as f:
                f.write(content)
            return True
        except OSError:
            return False

    @staticmethod
    def exists(path: str) -> bool:
        """Check if a file or directory exists."""
        full = path if os.path.isabs(path) else os.path.join(FileSystem.app_dir(), path)
        return os.path.exists(full)

    @staticmethod
    def delete(path: str) -> bool:
        """Delete a file. Returns ``True`` on success."""
        full = path if os.path.isabs(path) else os.path.join(FileSystem.app_dir(), path)
        try:
            os.remove(full)
            return True
        except OSError:
            return False

    @staticmethod
    def list_dir(path: str = "") -> list:
        """List entries in a directory."""
        full = path if os.path.isabs(path) else os.path.join(FileSystem.app_dir(), path)
        try:
            return os.listdir(full)
        except OSError:
            return []

    @staticmethod
    def read_bytes(path: str) -> Optional[bytes]:
        """Read a binary file."""
        full = path if os.path.isabs(path) else os.path.join(FileSystem.app_dir(), path)
        try:
            with open(full, "rb") as f:
                return f.read()
        except OSError:
            return None

    @staticmethod
    def write_bytes(path: str, data: bytes) -> bool:
        """Write a binary file. Returns ``True`` on success."""
        full = path if os.path.isabs(path) else os.path.join(FileSystem.app_dir(), path)
        try:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as f:
                f.write(data)
            return True
        except OSError:
            return False

    @staticmethod
    def get_size(path: str) -> Optional[int]:
        """Return file size in bytes, or ``None`` if not found."""
        full = path if os.path.isabs(path) else os.path.join(FileSystem.app_dir(), path)
        try:
            return os.path.getsize(full)
        except OSError:
            return None

    @staticmethod
    def ensure_dir(path: str) -> bool:
        """Create a directory (and parents) if it doesn't exist."""
        full = path if os.path.isabs(path) else os.path.join(FileSystem.app_dir(), path)
        try:
            os.makedirs(full, exist_ok=True)
            return True
        except OSError:
            return False

    @staticmethod
    def join(*parts: Any) -> str:
        """Join path components."""
        return os.path.join(*[str(p) for p in parts])
