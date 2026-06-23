"""The PythonNative Go shell UI, written in PythonNative.

This module is the screen host's root component while the app is *not* running:
the connect screen (enter or scan a dev-server URL), a loading screen during
download, and a red error screen. Once
[`DevSession`][pythonnative.dev.session.DevSession] reaches the ``connected``
phase it re-points the host at the user's entry module, so this UI is only ever
on screen between runs.

The native PythonNative Go templates mount this via
[`screen.create_dev_client_host`][pythonnative.screen]; its dotted entry path is
[`screen.DEV_CLIENT_ENTRY`][pythonnative.screen] (``"pythonnative.dev.ui"``),
and ``App`` is the conventional entry attribute.
"""

from __future__ import annotations

from typing import Any, Callable, List

import pythonnative as pn

from ..element import Element
from . import session as dev_session
from .session import PHASE_CONNECTING, PHASE_ERROR

_BG = "#0b1021"
_CARD = "#161c33"
_ACCENT = "#4f8cff"
_TEXT = "#f5f7ff"
_MUTED = "#9aa6c7"
_ERROR_BG = "#2a0e12"
_ERROR_ACCENT = "#ff5c66"


def _connect_handler(session: dev_session.DevSession, url: str) -> Callable[[], None]:
    """Return a zero-arg click handler that connects ``session`` to ``url``."""
    return lambda: session.connect(url)


@pn.component
def App() -> Element:
    """Render the connect / loading / error shell for PythonNative Go.

    Subscribes to the global [`DevSession`][pythonnative.dev.session.DevSession]
    so any phase change re-renders this component, then dispatches to the view
    for the current phase.

    Returns:
        The element tree for the current connection phase.
    """
    session = dev_session.get_session()
    _, set_tick = pn.use_state(0)

    def _subscribe() -> Callable[[], None]:
        return session.subscribe(lambda: set_tick(lambda value: value + 1))

    pn.use_effect(_subscribe, [])

    recent = session.recent_servers()
    initial_url = recent[0] if recent else ""
    url, set_url = pn.use_state(initial_url)

    if session.phase == PHASE_CONNECTING:
        return _loading_view(session.base_url or "the dev server")
    if session.phase == PHASE_ERROR:
        return _error_view(session)
    return _connect_view(session, url, set_url, recent)


def _connect_view(
    session: dev_session.DevSession,
    url: str,
    set_url: Callable[[Any], None],
    recent: List[str],
) -> Element:
    """Render the connect screen with URL entry, scan, and recent servers."""
    children: List[Element] = [
        pn.Text("PythonNative Go", style={"font_size": 28, "bold": True, "color": _TEXT}),
        pn.Text(
            "Run `pn start` in your project, then enter the URL it prints below " "(or tap a recent server).",
            style={"font_size": 15, "color": _MUTED},
        ),
        pn.TextInput(
            value=url,
            on_change=set_url,
            placeholder="http://192.168.0.10:8765",
            keyboard_type="url",
            auto_capitalize="none",
            style={
                "color": _TEXT,
                "background_color": _CARD,
                "padding": 14,
                "border_radius": 10,
                "font_size": 16,
            },
        ),
        pn.Button(
            "Connect",
            on_click=lambda: session.connect(url),
            style={"background_color": _ACCENT, "color": "#ffffff", "padding": 14, "border_radius": 10},
        ),
    ]

    if session.has_scanner():
        children.append(
            pn.Button(
                "Scan QR code",
                on_click=session.request_scan,
                style={"background_color": _CARD, "color": _TEXT, "padding": 14, "border_radius": 10},
            )
        )

    if recent:
        children.append(pn.Text("Recent", style={"font_size": 13, "color": _MUTED, "margin_top": 8}))
        for server in recent:
            children.append(
                pn.Button(
                    server,
                    on_click=_connect_handler(session, server),
                    style={"background_color": _CARD, "color": _ACCENT, "padding": 12, "border_radius": 10},
                )
            )

    return pn.ScrollView(
        pn.Column(*children, style={"spacing": 14, "padding": 24, "align_items": "stretch"}),
        style={"flex": 1, "background_color": _BG},
    )


def _loading_view(target: str) -> Element:
    """Render the loading screen shown while a bundle downloads."""
    return pn.Column(
        pn.ActivityIndicator(animating=True, color=_ACCENT, size="large"),
        pn.Text(f"Connecting to {target}...", style={"font_size": 16, "color": _TEXT, "margin_top": 16}),
        style={"flex": 1, "justify_content": "center", "align_items": "center", "background_color": _BG},
    )


def _error_view(session: dev_session.DevSession) -> Element:
    """Render the red error screen with the failure and retry/disconnect."""
    return pn.Column(
        pn.Text("Couldn't load the app", style={"font_size": 22, "bold": True, "color": _TEXT}),
        pn.ScrollView(
            pn.Text(session.error or "Unknown error.", style={"font_size": 13, "color": _TEXT}),
            style={"flex": 1, "background_color": "#00000033", "border_radius": 10, "padding": 12},
        ),
        pn.Row(
            pn.Button(
                "Try again",
                on_click=lambda: session.connect(session.base_url),
                style={
                    "flex": 1,
                    "background_color": "#ffffff",
                    "color": _ERROR_BG,
                    "padding": 14,
                    "border_radius": 10,
                },
            ),
            pn.Button(
                "Disconnect",
                on_click=session.disconnect,
                style={
                    "flex": 1,
                    "background_color": _ERROR_ACCENT,
                    "color": "#ffffff",
                    "padding": 14,
                    "border_radius": 10,
                },
            ),
            style={"spacing": 12},
        ),
        style={"flex": 1, "spacing": 16, "padding": 24, "background_color": _ERROR_BG, "justify_content": "center"},
    )
