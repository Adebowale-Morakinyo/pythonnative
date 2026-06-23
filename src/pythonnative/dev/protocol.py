"""Wire protocol shared by the PythonNative dev server and dev client.

``pn start`` runs a [`DevServer`][pythonnative.dev.server.DevServer] on the
developer's machine; the **PythonNative Go** app (or any debug build) runs a
[`DevClient`][pythonnative.dev.client.DevClient] on the device. They speak the
small HTTP protocol described here:

- ``GET /status`` -> JSON [`ServerStatus`][pythonnative.dev.protocol.ServerStatus]
  (handshake: protocol + SDK version, app name, entry module, current version).
- ``GET /manifest.json`` -> JSON [`Manifest`][pythonnative.dev.protocol.Manifest]
  (every bundled file plus its SHA-256 and size, so the client can sync only
  what changed).
- ``GET /files/<path>`` -> the raw bytes of one bundled file.
- ``GET /bundle.zip`` -> the whole bundle as a zip (fast initial download).
- ``GET /poll?since=<version>`` -> long-polls and returns a JSON
  [`PollResult`][pythonnative.dev.protocol.PollResult] when the bundle version
  changes (the developer saved a file), or after a timeout.

Keeping the schema in one module means the host and device sides can't drift.
Everything here is pure standard library so the device side stays
dependency-free (it has to import under Chaquopy and the embedded iOS
interpreter).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

PROTOCOL_VERSION = 1
"""Bumped whenever the wire format changes incompatibly."""

DEFAULT_PORT = 8765
"""Default TCP port for the dev server (overridable with ``pn start --port``)."""

SERVER_NAME = "pythonnative-dev"
"""Identifier returned by ``/status`` so clients can sanity-check the peer."""

# -- Endpoint paths -----------------------------------------------------

PATH_ROOT = "/"
PATH_STATUS = "/status"
PATH_MANIFEST = "/manifest.json"
PATH_BUNDLE_ZIP = "/bundle.zip"
PATH_FILES_PREFIX = "/files/"
PATH_POLL = "/poll"

POLL_TIMEOUT_SECONDS = 25.0
"""How long ``/poll`` blocks before returning the unchanged version."""


def hash_bytes(data: bytes) -> str:
    """Return the hex SHA-256 digest of ``data``.

    Args:
        data: The bytes to hash.

    Returns:
        The lowercase hex digest, used as a per-file content fingerprint
        in the [`Manifest`][pythonnative.dev.protocol.Manifest].
    """
    return hashlib.sha256(data).hexdigest()


def is_compatible(server_protocol: int, client_protocol: int = PROTOCOL_VERSION) -> bool:
    """Return whether a client and server can talk to each other.

    The protocol is versioned as a single integer; a mismatch means the
    PythonNative Go build is older or newer than the ``pn`` CLI and the
    user should update one of them.

    Args:
        server_protocol: ``protocol_version`` reported by ``/status``.
        client_protocol: The protocol version compiled into the client
            (defaults to this module's
            [`PROTOCOL_VERSION`][pythonnative.dev.protocol.PROTOCOL_VERSION]).

    Returns:
        ``True`` when the two versions match exactly.
    """
    return server_protocol == client_protocol


@dataclass(frozen=True)
class FileEntry:
    """One file in a bundle manifest.

    Attributes:
        path: Bundle-relative POSIX path (e.g. ``"app/main.py"``).
        sha256: Hex SHA-256 of the file contents.
        size: File size in bytes.
    """

    path: str
    sha256: str
    size: int

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable mapping for this entry."""
        return {"path": self.path, "sha256": self.sha256, "size": self.size}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileEntry":
        """Build a [`FileEntry`][pythonnative.dev.protocol.FileEntry] from ``data``."""
        return cls(path=str(data["path"]), sha256=str(data["sha256"]), size=int(data["size"]))


@dataclass
class Manifest:
    """The complete description of a served app bundle.

    A client compares a freshly fetched manifest against the one it last
    installed: files whose ``sha256`` changed (or that are new) are
    downloaded, files that disappeared are deleted from the overlay.

    Attributes:
        protocol_version: Wire protocol version (see
            [`PROTOCOL_VERSION`][pythonnative.dev.protocol.PROTOCOL_VERSION]).
        sdk_version: ``pythonnative.__version__`` on the host, so the client
            can warn about an SDK mismatch with the bundled framework.
        app_name: Human-readable project name (for the connect UI).
        entry_module: Dotted entry module to mount (e.g. ``"app.main"``).
        version: Opaque, monotonically increasing token bumped on every
            change. The client treats it as an equality token only.
        files: Every file in the bundle.
    """

    protocol_version: int
    sdk_version: str
    app_name: str
    entry_module: str
    version: str
    files: List[FileEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable mapping for this manifest."""
        return {
            "protocol_version": self.protocol_version,
            "sdk_version": self.sdk_version,
            "app_name": self.app_name,
            "entry_module": self.entry_module,
            "version": self.version,
            "files": [entry.to_dict() for entry in self.files],
        }

    def to_json(self) -> str:
        """Serialize this manifest to a JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Manifest":
        """Build a [`Manifest`][pythonnative.dev.protocol.Manifest] from ``data``."""
        return cls(
            protocol_version=int(data.get("protocol_version", 0)),
            sdk_version=str(data.get("sdk_version", "")),
            app_name=str(data.get("app_name", "")),
            entry_module=str(data.get("entry_module", "app.main")),
            version=str(data.get("version", "")),
            files=[FileEntry.from_dict(item) for item in data.get("files", [])],
        )

    @classmethod
    def from_json(cls, text: str) -> "Manifest":
        """Parse a manifest from a JSON string."""
        return cls.from_dict(json.loads(text))

    def by_path(self) -> Dict[str, FileEntry]:
        """Return a ``{path: entry}`` index of this manifest's files."""
        return {entry.path: entry for entry in self.files}


@dataclass
class ServerStatus:
    """The ``/status`` handshake payload.

    Attributes:
        server: Always [`SERVER_NAME`][pythonnative.dev.protocol.SERVER_NAME];
            lets a client confirm it reached a PythonNative dev server.
        protocol_version: Wire protocol version.
        sdk_version: Host ``pythonnative.__version__``.
        app_name: Project name.
        entry_module: Dotted entry module to mount.
        version: Current bundle version token.
    """

    server: str
    protocol_version: int
    sdk_version: str
    app_name: str
    entry_module: str
    version: str

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable mapping for this status."""
        return {
            "server": self.server,
            "protocol_version": self.protocol_version,
            "sdk_version": self.sdk_version,
            "app_name": self.app_name,
            "entry_module": self.entry_module,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerStatus":
        """Build a [`ServerStatus`][pythonnative.dev.protocol.ServerStatus] from ``data``."""
        return cls(
            server=str(data.get("server", "")),
            protocol_version=int(data.get("protocol_version", 0)),
            sdk_version=str(data.get("sdk_version", "")),
            app_name=str(data.get("app_name", "")),
            entry_module=str(data.get("entry_module", "app.main")),
            version=str(data.get("version", "")),
        )

    @classmethod
    def from_json(cls, text: str) -> "ServerStatus":
        """Parse a status payload from a JSON string."""
        return cls.from_dict(json.loads(text))

    def is_pythonnative(self) -> bool:
        """Return whether the peer identified itself as a PythonNative server."""
        return self.server == SERVER_NAME


@dataclass
class PollResult:
    """The ``/poll`` response describing the latest bundle version.

    Attributes:
        version: The current bundle version token. When it differs from the
            ``since`` value the client sent, the client re-fetches the
            manifest and syncs changed files.
        changed: Whether the version advanced during this poll (a
            convenience flag; clients may also just compare ``version``).
    """

    version: str
    changed: bool

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable mapping for this poll result."""
        return {"version": self.version, "changed": self.changed}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PollResult":
        """Build a [`PollResult`][pythonnative.dev.protocol.PollResult] from ``data``."""
        return cls(version=str(data.get("version", "")), changed=bool(data.get("changed", False)))

    @classmethod
    def from_json(cls, text: str) -> "PollResult":
        """Parse a poll result from a JSON string."""
        return cls.from_dict(json.loads(text))
