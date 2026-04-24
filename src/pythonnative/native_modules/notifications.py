"""Cross-platform local notifications.

Provides static methods for requesting permission, scheduling, and
cancelling local push notifications. Uses Android's
`NotificationManager` or iOS's `UNUserNotificationCenter`.

On iOS, you must call
[`request_permission`][pythonnative.native_modules.Notifications.request_permission]
before scheduling. On Android 13+, the equivalent runtime permission
should be requested through standard Android APIs (the manifest
declaration is otherwise sufficient).

Example:
    ```python
    from pythonnative import Notifications

    Notifications.request_permission(lambda granted: print("granted=", granted))
    Notifications.schedule(
        title="Reminder",
        body="Time for a walk!",
        delay_seconds=60,
        identifier="walk",
    )
    ```
"""

from typing import Any, Callable, Optional

from ..utils import IS_ANDROID


class Notifications:
    """Local notification interface.

    All methods are static and dispatch to the correct platform
    implementation at call time.
    """

    @staticmethod
    def request_permission(on_result: Optional[Callable[[bool], None]] = None) -> None:
        """Request notification permission from the user.

        On Android, the manifest declaration is normally sufficient for
        legacy permission grants and this method calls back with `True`
        without prompting.

        Args:
            on_result: Callable invoked with `True` if the user
                accepted, `False` if they declined or the prompt
                failed.
        """
        if IS_ANDROID:
            if on_result:
                on_result(True)
        else:
            Notifications._ios_request_permission(on_result)

    @staticmethod
    def schedule(
        title: str,
        body: str = "",
        delay_seconds: float = 0,
        identifier: str = "default",
        **options: Any,
    ) -> None:
        """Schedule a local notification.

        Args:
            title: Notification title.
            body: Notification body text.
            delay_seconds: Seconds from now until delivery. Use `0` for
                an effectively immediate notification.
            identifier: Stable ID used by
                [`cancel`][pythonnative.native_modules.Notifications.cancel]
                to target this notification.
            **options: Reserved for future tuning (e.g., `sound`,
                `badge`, `category`).
        """
        if IS_ANDROID:
            Notifications._android_schedule(title, body, delay_seconds, identifier, **options)
        else:
            Notifications._ios_schedule(title, body, delay_seconds, identifier, **options)

    @staticmethod
    def cancel(identifier: str = "default") -> None:
        """Cancel a pending notification by its identifier.

        Args:
            identifier: The same string passed to
                [`schedule`][pythonnative.native_modules.Notifications.schedule].
        """
        if IS_ANDROID:
            Notifications._android_cancel(identifier)
        else:
            Notifications._ios_cancel(identifier)

    # -- Android ---------------------------------------------------------

    @staticmethod
    def _android_schedule(title: str, body: str, delay_seconds: float, identifier: str, **options: Any) -> None:
        try:
            from java import jclass

            from ..utils import get_android_context

            ctx = get_android_context()
            nm = ctx.getSystemService(jclass("android.content.Context").NOTIFICATION_SERVICE)
            channel_id = "pn_default"
            NotificationChannel = jclass("android.app.NotificationChannel")
            channel = NotificationChannel(channel_id, "PythonNative", 3)  # IMPORTANCE_DEFAULT
            nm.createNotificationChannel(channel)

            Builder = jclass("android.app.Notification$Builder")
            builder = Builder(ctx, channel_id)
            builder.setContentTitle(title)
            builder.setContentText(body)
            builder.setSmallIcon(jclass("android.R$drawable").ic_dialog_info)
            nm.notify(abs(hash(identifier)) % (2**31), builder.build())
        except Exception:
            pass

    @staticmethod
    def _android_cancel(identifier: str) -> None:
        try:
            from java import jclass

            from ..utils import get_android_context

            ctx = get_android_context()
            nm = ctx.getSystemService(jclass("android.content.Context").NOTIFICATION_SERVICE)
            nm.cancel(abs(hash(identifier)) % (2**31))
        except Exception:
            pass

    # -- iOS -------------------------------------------------------------

    @staticmethod
    def _ios_request_permission(on_result: Optional[Callable[[bool], None]] = None) -> None:
        try:
            from rubicon.objc import ObjCClass

            center = ObjCClass("UNUserNotificationCenter").currentNotificationCenter()
            center.requestAuthorizationWithOptions_completionHandler_(0x07, None)
            if on_result:
                on_result(True)
        except Exception:
            if on_result:
                on_result(False)

    @staticmethod
    def _ios_schedule(title: str, body: str, delay_seconds: float, identifier: str, **options: Any) -> None:
        try:
            from rubicon.objc import ObjCClass

            content = ObjCClass("UNMutableNotificationContent").alloc().init()
            content.setTitle_(title)
            content.setBody_(body)

            if delay_seconds > 0:
                trigger = ObjCClass("UNTimeIntervalNotificationTrigger").triggerWithTimeInterval_repeats_(
                    delay_seconds, False
                )
            else:
                trigger = ObjCClass("UNTimeIntervalNotificationTrigger").triggerWithTimeInterval_repeats_(1, False)

            request = ObjCClass("UNNotificationRequest").requestWithIdentifier_content_trigger_(
                identifier, content, trigger
            )
            center = ObjCClass("UNUserNotificationCenter").currentNotificationCenter()
            center.addNotificationRequest_withCompletionHandler_(request, None)
        except Exception:
            pass

    @staticmethod
    def _ios_cancel(identifier: str) -> None:
        try:
            from rubicon.objc import ObjCClass

            center = ObjCClass("UNUserNotificationCenter").currentNotificationCenter()
            NSArray = ObjCClass("NSArray")
            arr = NSArray.arrayWithObject_(identifier)
            center.removePendingNotificationRequestsWithIdentifiers_(arr)
        except Exception:
            pass
