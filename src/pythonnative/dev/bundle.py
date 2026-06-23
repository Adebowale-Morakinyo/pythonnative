"""Package a PythonNative project into a servable bundle.

The dev server serves the user's ``app/`` directory (and, optionally, a
directory of pure-Python dependencies) to the PythonNative Go client. A
[`Bundle`][pythonnative.dev.bundle.Bundle] is a content-addressed view over
those files: it can produce a
[`Manifest`][pythonnative.dev.protocol.Manifest] (paths + SHA-256 + size),
read any single file, or zip the whole thing for a fast first download.

Only *sources and assets* are bundled. The ``pythonnative`` framework itself is
baked into the Go client, so it is never part of a bundle; this is exactly what
makes one prebuilt client able to run any pure-Python PythonNative app.
"""

from __future__ import annotations

import io
import os
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .protocol import PROTOCOL_VERSION, FileEntry, Manifest, hash_bytes

APP_DIR = "app"
"""Bundle-relative root for the user's application sources."""

SITE_PACKAGES_DIR = "site-packages"
"""Bundle-relative root for optional pure-Python dependencies."""

# Files/directories never worth shipping to a device.
_IGNORED_DIRS = frozenset({"__pycache__", ".git", ".hg", ".svn", "build", ".venv", "venv", ".mypy_cache"})
_IGNORED_SUFFIXES = (".pyc", ".pyo", ".pyd")
_IGNORED_NAMES = frozenset({".DS_Store"})


def _should_skip(name: str) -> bool:
    if name in _IGNORED_NAMES:
        return True
    return name.endswith(_IGNORED_SUFFIXES)


def _collect(root: Path, prefix: str) -> Dict[str, Path]:
    """Walk ``root`` returning ``{bundle_path: absolute_path}``.

    Args:
        root: Directory to walk.
        prefix: Bundle-relative prefix to prepend to each discovered file
            (e.g. ``"app"``).

    Returns:
        A mapping from POSIX bundle paths to absolute filesystem paths,
        skipping caches, VCS metadata, and compiled artifacts.
    """
    files: Dict[str, Path] = {}
    if not root.is_dir():
        return files
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _IGNORED_DIRS and not d.startswith(".")]
        for filename in filenames:
            if _should_skip(filename):
                continue
            absolute = Path(dirpath) / filename
            relative = absolute.relative_to(root).as_posix()
            files[f"{prefix}/{relative}"] = absolute
    return files


def new_version() -> str:
    """Return a fresh, monotonically increasing bundle version token."""
    return str(time.time_ns())


@dataclass
class Bundle:
    """A content-addressed snapshot of a project's servable files.

    Attributes:
        app_name: Project name shown in the client connect UI.
        entry_module: Dotted entry module the client mounts (e.g. ``"app.main"``).
        files: ``{bundle_path: absolute_path}`` for every served file.
        version: Opaque version token for this snapshot.
        sdk_version: Host ``pythonnative.__version__``.
    """

    app_name: str
    entry_module: str
    files: Dict[str, Path]
    version: str
    sdk_version: str

    def manifest(self) -> Manifest:
        """Compute the [`Manifest`][pythonnative.dev.protocol.Manifest] for this bundle.

        Reads every file to hash it, so callers should treat this as
        moderately expensive and cache the result between changes.

        Returns:
            A manifest listing every file with its SHA-256 and size.
        """
        entries: List[FileEntry] = []
        for bundle_path in sorted(self.files):
            data = self.read(bundle_path)
            entries.append(FileEntry(path=bundle_path, sha256=hash_bytes(data), size=len(data)))
        return Manifest(
            protocol_version=PROTOCOL_VERSION,
            sdk_version=self.sdk_version,
            app_name=self.app_name,
            entry_module=self.entry_module,
            version=self.version,
            files=entries,
        )

    def read(self, bundle_path: str) -> bytes:
        """Return the bytes of one bundled file.

        Args:
            bundle_path: A POSIX bundle path present in ``files``.

        Returns:
            The file contents.

        Raises:
            KeyError: If ``bundle_path`` is not part of this bundle.
        """
        absolute = self.files.get(bundle_path)
        if absolute is None:
            raise KeyError(bundle_path)
        return absolute.read_bytes()

    def zip_bytes(self) -> bytes:
        """Return the entire bundle as an in-memory zip archive.

        Returns:
            A zip whose members are the bundle paths, suitable for the
            client's ``/bundle.zip`` fast path.
        """
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for bundle_path in sorted(self.files):
                archive.writestr(bundle_path, self.read(bundle_path))
        return buffer.getvalue()


def build_bundle(
    project_root: Path,
    *,
    app_name: str,
    entry_module: str,
    sdk_version: str,
    site_packages: Optional[Path] = None,
    version: Optional[str] = None,
) -> Bundle:
    """Construct a [`Bundle`][pythonnative.dev.bundle.Bundle] from a project.

    Args:
        project_root: The directory containing ``app/``.
        app_name: Project name for the connect UI.
        entry_module: Dotted entry module to mount on the device.
        sdk_version: Host ``pythonnative.__version__``.
        site_packages: Optional directory of pure-Python dependencies to
            include under ``site-packages/`` (typically produced by
            ``pip install -t`` for ``[requirements].packages``).
        version: Optional explicit version token; a fresh one is generated
            when omitted.

    Returns:
        A bundle ready to serve.
    """
    files = _collect(project_root / APP_DIR, APP_DIR)
    if site_packages is not None:
        files.update(_collect(site_packages, SITE_PACKAGES_DIR))
    return Bundle(
        app_name=app_name,
        entry_module=entry_module,
        files=files,
        version=version or new_version(),
        sdk_version=sdk_version,
    )
