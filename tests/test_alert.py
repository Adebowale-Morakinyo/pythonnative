"""Unit tests for the imperative Alert API."""

from __future__ import annotations

from typing import Generator

import pytest

from pythonnative.alerts import Alert
from pythonnative.platform import _set_platform_for_test


@pytest.fixture(autouse=True)
def _reset() -> Generator[None, None, None]:
    Alert._test_log.clear()
    yield
    Alert._test_log.clear()
    _set_platform_for_test(None)


def test_show_records_to_test_log() -> None:
    Alert.show(title="Hello", message="World")
    assert len(Alert._test_log) == 1
    entry = Alert._test_log[0]
    assert entry["title"] == "Hello"
    assert entry["message"] == "World"
    assert entry["style"] == "alert"
    assert entry["buttons"] == []


def test_show_with_buttons_and_action_sheet_style() -> None:
    Alert.show(
        title="Pick",
        buttons=[
            {"label": "A", "on_press": lambda: None},
            {"label": "B", "style": "destructive"},
        ],
        style="action_sheet",
    )
    entry = Alert._test_log[0]
    assert entry["style"] == "action_sheet"
    assert len(entry["buttons"]) == 2
    assert entry["buttons"][0]["label"] == "A"
    assert entry["buttons"][1]["style"] == "destructive"


def test_confirm_creates_two_buttons() -> None:
    Alert.confirm(title="Sure?", on_confirm=lambda: None)
    entry = Alert._test_log[0]
    assert len(entry["buttons"]) == 2
    assert entry["buttons"][0]["label"] == "Cancel"
    assert entry["buttons"][0]["style"] == "cancel"
    assert entry["buttons"][1]["label"] == "OK"
    assert entry["buttons"][1]["style"] == "default"


def test_confirm_custom_labels() -> None:
    Alert.confirm(
        title="Quit?",
        message="Unsaved changes will be lost.",
        confirm_label="Quit",
        cancel_label="Stay",
    )
    entry = Alert._test_log[0]
    assert entry["title"] == "Quit?"
    assert entry["message"] == "Unsaved changes will be lost."
    assert entry["buttons"][0]["label"] == "Stay"
    assert entry["buttons"][1]["label"] == "Quit"
