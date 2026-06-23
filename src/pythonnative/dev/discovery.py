"""Best-effort detection of the machine's LAN address for ``pn start``.

The dev server binds to all interfaces, but the PythonNative Go app on a phone
needs a concrete address to connect to. ``0.0.0.0`` and ``127.0.0.1`` are
useless to another device, so this module finds the primary outbound IPv4
address (the one a packet to the internet would leave from) without actually
sending anything.
"""

from __future__ import annotations

import socket


def lan_ip() -> str:
    """Return this machine's primary LAN IPv4 address.

    Opens a UDP socket "connected" to a public address so the OS picks the
    interface it would route through, then reads back the local address. No
    packets are sent. Falls back to ``127.0.0.1`` if detection fails (for
    example with no network), which still works for an iOS simulator.

    Returns:
        A dotted-quad IPv4 string reachable from devices on the same LAN.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return str(sock.getsockname()[0])
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"
    finally:
        sock.close()


def server_url(host: str, port: int) -> str:
    """Format an ``http://host:port`` base URL for the dev server.

    Args:
        host: Hostname or IP the client should connect to.
        port: TCP port the dev server listens on.

    Returns:
        The base URL string (no trailing slash).
    """
    return f"http://{host}:{port}"
