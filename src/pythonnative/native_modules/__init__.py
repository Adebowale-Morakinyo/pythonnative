"""Native API modules for device capabilities.

Provides cross-platform Python interfaces to common device APIs:

- [`Camera`][pythonnative.native_modules.Camera]: photo capture and
  gallery picking.
- [`Location`][pythonnative.native_modules.Location]: GPS and
  location services.
- [`FileSystem`][pythonnative.native_modules.FileSystem]: app-scoped
  file I/O.
- [`Notifications`][pythonnative.native_modules.Notifications]: local
  push notifications.

Each module auto-detects the platform at import time and dispatches to
the appropriate native APIs via Chaquopy (Android) or rubicon-objc (iOS).
On a desktop machine without either runtime, the modules raise
informative `RuntimeError` instances when called.
"""

from .camera import Camera
from .file_system import FileSystem
from .location import Location
from .notifications import Notifications

__all__ = ["Camera", "FileSystem", "Location", "Notifications"]
