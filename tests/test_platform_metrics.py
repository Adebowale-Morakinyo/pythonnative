"""Unit tests for platform_metrics: dimensions, keyboard, subscribers."""

from __future__ import annotations

from typing import Generator

import pytest

from pythonnative import platform_metrics as pm


@pytest.fixture(autouse=True)
def _reset() -> Generator[None, None, None]:
    pm.reset_safe_area_insets()
    pm.reset_window_dimensions()
    pm.reset_keyboard_height()
    yield
    pm.reset_safe_area_insets()
    pm.reset_window_dimensions()
    pm.reset_keyboard_height()


# ======================================================================
# Window dimensions
# ======================================================================


def test_window_dimensions_default_zero() -> None:
    dims = pm.get_window_dimensions()
    assert dims.width == 0.0
    assert dims.height == 0.0


def test_set_window_dimensions_clamps_negative() -> None:
    pm.set_window_dimensions(-1.0, -2.0)
    dims = pm.get_window_dimensions()
    assert dims.width == 0.0
    assert dims.height == 0.0


def test_set_window_dimensions_updates() -> None:
    pm.set_window_dimensions(390.0, 844.0)
    dims = pm.get_window_dimensions()
    assert dims.width == 390.0
    assert dims.height == 844.0


# ======================================================================
# Keyboard height
# ======================================================================


def test_keyboard_height_default_zero() -> None:
    assert pm.get_keyboard_height() == 0.0


def test_keyboard_height_clamps_negative() -> None:
    pm.set_keyboard_height(-50.0)
    assert pm.get_keyboard_height() == 0.0


def test_keyboard_height_updates() -> None:
    pm.set_keyboard_height(280.0)
    assert pm.get_keyboard_height() == 280.0


# ======================================================================
# Subscribers
# ======================================================================


def test_subscribe_fires_on_window_change() -> None:
    received: list = []
    pm.subscribe(lambda: received.append("tick"))
    pm.set_window_dimensions(100, 200)
    assert received == ["tick"]


def test_subscribe_fires_on_keyboard_change() -> None:
    received: list = []
    pm.subscribe(lambda: received.append("tick"))
    pm.set_keyboard_height(100)
    assert received == ["tick"]


def test_subscribe_fires_on_safe_area_change() -> None:
    received: list = []
    pm.subscribe(lambda: received.append("tick"))
    pm.set_safe_area_insets(top=44.0, left=0.0, bottom=34.0, right=0.0)
    assert received == ["tick"]


def test_subscribe_skips_no_op_updates() -> None:
    received: list = []
    pm.subscribe(lambda: received.append("tick"))
    pm.set_window_dimensions(100, 200)
    pm.set_window_dimensions(100, 200)  # same value
    assert received == ["tick"]


def test_unsubscribe_stops_notifications() -> None:
    received: list = []
    unsub = pm.subscribe(lambda: received.append("tick"))
    pm.set_keyboard_height(100)
    unsub()
    pm.set_keyboard_height(200)
    assert received == ["tick"]


def test_subscriber_exception_isolated() -> None:
    received: list = []

    def boom() -> None:
        raise RuntimeError("boom")

    pm.subscribe(boom)
    pm.subscribe(lambda: received.append("ok"))
    pm.set_window_dimensions(50, 60)
    assert received == ["ok"]
