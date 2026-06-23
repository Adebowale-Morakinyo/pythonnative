"""Resolve and create the app's root screen host for the native templates.

Native templates (Android ``ScreenFragment`` / iOS ``ViewController``) used to
hard-code ``"app.main"`` as the first screen. They now call
[`create_root_host`][pythonnative.bootstrap.create_root_host] instead, which
reads a tiny ``pn_entry`` module written into the bundle at build time to decide
what to mount:

- A **normal build** mounts the configured ``entry_point`` (so
  ``app.entry_point`` in ``pythonnative.toml`` is finally honored).
- A **PythonNative Go** build (``pn go build``) mounts the dev-client shell
  (``pythonnative.dev.ui``), which downloads and runs any project over the
  network.

Pushed navigation screens still go through
[`create_screen`][pythonnative.screen.create_screen] with an explicit path; only
the root is resolved here.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

DEFAULT_ENTRY = "app.main"
"""Entry module used when no ``pn_entry`` marker is present (dev checkouts/tests)."""


def _read_entry() -> Tuple[str, bool]:
    """Return ``(entry_module, dev_client)`` from the generated ``pn_entry`` module."""
    try:
        import pn_entry
    except Exception:
        return DEFAULT_ENTRY, False
    entry = str(getattr(pn_entry, "ENTRY_MODULE", DEFAULT_ENTRY)) or DEFAULT_ENTRY
    dev_client = bool(getattr(pn_entry, "DEV_CLIENT", False))
    return entry, dev_client


def root_entry_module() -> str:
    """Return the dotted path of the root component the app should mount.

    Returns:
        The configured entry module, or the dev-client shell entry for a
        PythonNative Go build.
    """
    from .screen import DEV_CLIENT_ENTRY

    entry, dev_client = _read_entry()
    return DEV_CLIENT_ENTRY if dev_client else entry


def create_root_host(native_instance: Any = None, args_json: Optional[str] = None) -> Any:
    """Create the root screen host for the current build.

    Args:
        native_instance: The native ``Activity`` / ``UIViewController`` owner.
        args_json: Optional JSON navigation arguments for the root screen.

    Returns:
        A screen host: the dev-client shell for a PythonNative Go build, or the
        configured entry component otherwise.
    """
    from . import screen

    entry, dev_client = _read_entry()
    if dev_client:
        return screen.create_dev_client_host(native_instance, args_json)
    return screen.create_screen(entry, native_instance, args_json)
