"""Cross-platform location / GPS access.

Provides static methods for requesting the device's current
coordinates. Uses Android's `LocationManager` or iOS's
`CLLocationManager`. Permission prompts are triggered by the system the
first time a location-using API is called; ensure the appropriate
manifest entries (`android.permission.ACCESS_FINE_LOCATION`) and
Info.plist keys (`NSLocationWhenInUseUsageDescription`) are present.

Example:
    ```python
    from pythonnative import Location

    def handle(coords):
        if coords is None:
            print("Location unavailable")
        else:
            lat, lon = coords
            print(f"You are at {lat:.5f}, {lon:.5f}")

    Location.get_current(on_result=handle)
    ```
"""

from typing import Any, Callable, Optional, Tuple

from ..utils import IS_ANDROID


class Location:
    """GPS / location-services interface.

    All methods are static and dispatch to the correct platform
    implementation at call time.
    """

    @staticmethod
    def get_current(
        on_result: Optional[Callable[[Optional[Tuple[float, float]]], None]] = None,
        **options: Any,
    ) -> None:
        """Request the device's current location.

        Args:
            on_result: Callable invoked with `(latitude, longitude)`
                tuples, or `None` if no recent fix is available or the
                user denies permission.
            **options: Reserved for platform-specific tuning (e.g.,
                `accuracy`, `timeout`).
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
