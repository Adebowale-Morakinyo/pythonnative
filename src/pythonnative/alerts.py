"""Imperative system alerts.

Modeled on React Native's `Alert.alert()`. Alerts are not part of
the element tree — they're imperative, fire-and-forget calls that
trigger a native dialog.

Example:
    ```python
    import pythonnative as pn

    def confirm_delete():
        pn.Alert.show(
            title="Delete item?",
            message="This action cannot be undone.",
            buttons=[
                {"label": "Cancel", "style": "cancel"},
                {
                    "label": "Delete",
                    "style": "destructive",
                    "on_press": delete_item,
                },
            ],
        )
    ```
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .platform import Platform


class Alert:
    """Imperative alert / action-sheet helper.

    All methods are static. Use `Alert.show()` for an alert dialog
    and pass ``style="action_sheet"`` for an iOS-style action sheet.
    """

    @staticmethod
    def show(
        *,
        title: str,
        message: Optional[str] = None,
        buttons: Optional[List[Dict[str, Any]]] = None,
        style: str = "alert",
    ) -> None:
        """Present a native alert dialog or action sheet.

        Args:
            title: Dialog title (required).
            message: Optional body text.
            buttons: Each button is ``{"label": str, "style":
                "default"|"cancel"|"destructive", "on_press": callable}``.
                Defaults to a single "OK" button.
            style: ``"alert"`` (default) or ``"action_sheet"``.

        On iOS this uses ``UIAlertController``; on Android it uses
        ``AlertDialog.Builder``. On the test backend the call is a
        no-op so unit tests don't need to mock UIKit/AndroidX.
        """
        if Platform.is_ios:
            try:
                from .native_views.ios import _present_alert as _ios_present_alert

                _ios_present_alert(title=title, message=message, buttons=buttons or [], style=style)
            except Exception:
                pass
            return
        if Platform.is_android:
            try:
                from .native_views.android import _present_alert as _android_present_alert

                _android_present_alert(title=title, message=message, buttons=buttons or [], style=style)
            except Exception:
                pass
            return
        # Test environment: record the call so unit tests can assert on it.
        Alert._test_log.append(
            {
                "title": title,
                "message": message,
                "buttons": list(buttons or []),
                "style": style,
            }
        )

    @staticmethod
    def confirm(
        *,
        title: str,
        message: Optional[str] = None,
        confirm_label: str = "OK",
        cancel_label: str = "Cancel",
        on_confirm: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
    ) -> None:
        """Convenience wrapper for two-button confirm/cancel dialogs."""
        Alert.show(
            title=title,
            message=message,
            buttons=[
                {"label": cancel_label, "style": "cancel", "on_press": on_cancel},
                {"label": confirm_label, "style": "default", "on_press": on_confirm},
            ],
        )

    #: Records every Alert.show call when running off-device. Tests
    #: should reset this list between cases via
    #: ``Alert._test_log.clear()``.
    _test_log: List[Dict[str, Any]] = []
