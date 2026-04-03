"""Native API modules for device capabilities.

Provides cross-platform Python interfaces to common device APIs:

- :mod:`~.camera` — photo capture and gallery picking
- :mod:`~.location` — GPS / location services
- :mod:`~.file_system` — app-scoped file I/O
- :mod:`~.notifications` — local push notifications

Each module auto-detects the platform and calls the appropriate native
APIs via Chaquopy (Android) or rubicon-objc (iOS).
"""

from .camera import Camera
from .file_system import FileSystem
from .location import Location
from .notifications import Notifications

__all__ = ["Camera", "FileSystem", "Location", "Notifications"]
