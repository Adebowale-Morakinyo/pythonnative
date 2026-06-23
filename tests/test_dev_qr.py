"""Tests for the dependency-free QR encoder and LAN discovery helpers."""

import pytest

from pythonnative.dev import discovery, qr


def test_qr_matrix_is_square_and_versioned() -> None:
    matrix = qr.qr_matrix("http://192.168.1.20:8765")
    size = len(matrix)
    # Versions 1-4 are 21, 25, 29, 33 modules on a side.
    assert size in (21, 25, 29, 33)
    assert all(len(row) == size for row in matrix)


def test_qr_matrix_has_finder_patterns() -> None:
    matrix = qr.qr_matrix("http://10.0.0.2:8765")
    # Top-left finder pattern: a dark 7x7 border. Spot-check the corner.
    assert matrix[0][0] is True
    assert matrix[0][6] is True
    assert matrix[6][0] is True
    # Inner separator row is light.
    assert matrix[7][0] is False


def test_render_qr_returns_ansi_string() -> None:
    rendered = qr.render_qr("http://192.168.1.20:8765")
    assert rendered is not None
    assert "\x1b[" in rendered
    assert rendered.count("\n") > 10


def test_render_qr_returns_none_for_too_long_input() -> None:
    # Far beyond the ~78 byte capacity of a version-4 level-L code.
    assert qr.render_qr("x" * 500) is None


def test_qr_matrix_raises_for_too_long_input() -> None:
    with pytest.raises(ValueError):
        qr.qr_matrix("x" * 500)


def test_server_url_formats_base_url() -> None:
    assert discovery.server_url("192.168.1.20", 8765) == "http://192.168.1.20:8765"


def test_lan_ip_returns_dotted_quad() -> None:
    ip = discovery.lan_ip()
    parts = ip.split(".")
    assert len(parts) == 4
    assert all(part.isdigit() for part in parts)
