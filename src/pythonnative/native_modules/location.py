"""Cross-platform location / GPS access.

Provides methods for requesting the current device location.
Uses Android's ``LocationManager`` or iOS's ``CLLocationManager``.
"""

from typing import Any, Callable, Optional, Tuple

from ..utils import IS_ANDROID


class Location:
    """GPS / Location services interface."""

    @staticmethod
    def get_current(
        on_result: Optional[Callable[[Optional[Tuple[float, float]]], None]] = None,
        **options: Any,
    ) -> None:
        """Request the current location.

        Parameters
        ----------
        on_result:
            ``((lat, lon) | None) -> None`` called with coordinates or
            ``None`` if location is unavailable.
        """
        if IS_ANDROID:
            Location._android_get(on_result, **options)
        else:
            Location._ios_get(on_result, **options)

    @staticmethod
    def _android_get(on_result: Optional[Callable] = None, **options: Any) -> None:
        try:
            from java import jclass

            from ..utils import get_android_context

            ctx = get_android_context()
            lm = ctx.getSystemService(jclass("android.content.Context").LOCATION_SERVICE)
            loc = lm.getLastKnownLocation("gps")
            if loc and on_result:
                on_result((loc.getLatitude(), loc.getLongitude()))
            elif on_result:
                on_result(None)
        except Exception:
            if on_result:
                on_result(None)

    @staticmethod
    def _ios_get(on_result: Optional[Callable] = None, **options: Any) -> None:
        try:
            from rubicon.objc import ObjCClass

            lm = ObjCClass("CLLocationManager").alloc().init()
            lm.requestWhenInUseAuthorization()
            lm.startUpdatingLocation()
        except Exception:
            if on_result:
                on_result(None)
