"""PythonNative dev server and dev client (``pn start`` + PythonNative Go).

This package implements the Expo-style inner development loop:

- [`server`][pythonnative.dev.server] and [`bundle`][pythonnative.dev.bundle]
  run on the developer's machine behind ``pn start``: they package the project
  and serve it over HTTP with live reload.
- [`client`][pythonnative.dev.client], [`session`][pythonnative.dev.session],
  and [`ui`][pythonnative.dev.ui] run on the device inside the **PythonNative
  Go** app: they download the bundle, mount it, and Fast-Refresh on every save.
- [`protocol`][pythonnative.dev.protocol] is the small HTTP contract shared by
  both sides; [`qr`][pythonnative.dev.qr] and
  [`discovery`][pythonnative.dev.discovery] support the ``pn start`` terminal UX.

Submodules are imported explicitly by their consumers (the CLI on the host, the
native templates on the device) so importing this package stays cheap and free
of side effects.
"""

from __future__ import annotations

DEV_CLIENT_ENTRY = "pythonnative.dev.ui"
"""Dotted entry path of the PythonNative Go shell UI (connect/loading/error)."""
