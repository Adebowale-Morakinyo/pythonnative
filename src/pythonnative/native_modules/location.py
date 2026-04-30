"""Cross-platform location / GPS access.

Provides static methods for requesting the device's current
coordinates. Uses Android's `LocationManager` (with a transient
`LocationListener`) or iOS's `CLLocationManager` (with a strongly
retained `CLLocationManagerDelegate`). Permission prompts are
triggered the first time a location-using API is called; ensure the
appropriate manifest entries (`android.permission.ACCESS_FINE_LOCATION`)
and Info.plist keys (`NSLocationWhenInUseUsageDescription`) are
present.

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

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from ..utils import IS_ANDROID, IS_IOS

# Module-level retain pool so delegates aren't garbage-collected
# before the picker calls back. Keyed by id(delegate).
_pending_delegates: Dict[int, Any] = {}


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
            _android_get(on_result, **options)
        elif IS_IOS:
            _ios_get(on_result, **options)
        else:
            if on_result:
                on_result(None)


# ======================================================================
# iOS implementation: CLLocationManagerDelegate
# ======================================================================


def _ios_get(on_result: Optional[Callable], **options: Any) -> None:
    try:
        from rubicon.objc import ObjCClass, objc_method

        CLLocationManager = ObjCClass("CLLocationManager")
        NSObject = ObjCClass("NSObject")

        class _PNLocationDelegate(NSObject):  # type: ignore[misc,valid-type]
            _callback: Optional[Callable] = None
            _manager: Any = None
            _delivered: bool = False

            @objc_method
            def locationManager_didUpdateLocations_(self, manager: Any, locations: Any) -> None:
                if self._delivered:
                    return
                try:
                    last = locations.lastObject
                    if last is None:
                        return
                    coord = last.coordinate
                    lat = float(coord.latitude)
                    lon = float(coord.longitude)
                except Exception:
                    return
                self._delivered = True
                try:
                    manager.stopUpdatingLocation()
                except Exception:
                    pass
                if self._callback is not None:
                    try:
                        self._callback((lat, lon))
                    except Exception:
                        pass
                _pending_delegates.pop(id(self), None)

            @objc_method
            def locationManager_didFailWithError_(self, manager: Any, error: Any) -> None:
                if self._delivered:
                    return
                self._delivered = True
                try:
                    manager.stopUpdatingLocation()
                except Exception:
                    pass
                if self._callback is not None:
                    try:
                        self._callback(None)
                    except Exception:
                        pass
                _pending_delegates.pop(id(self), None)

            @objc_method
            def locationManagerDidChangeAuthorization_(self, manager: Any) -> None:
                # Authorization granted: kick off a single fix. If the
                # user denied access, the delegate's didFail callback
                # will fire and the result will be ``None``.
                try:
                    status = int(manager.authorizationStatus)
                except Exception:
                    status = 0
                if status in (3, 4):  # AuthorizedAlways, AuthorizedWhenInUse
                    try:
                        manager.startUpdatingLocation()
                    except Exception:
                        pass

        delegate = _PNLocationDelegate.new()
        delegate._callback = on_result
        _pending_delegates[id(delegate)] = delegate

        manager = CLLocationManager.alloc().init()
        manager.setDelegate_(delegate)
        delegate._manager = manager
        try:
            manager.requestWhenInUseAuthorization()
        except Exception:
            pass
        try:
            manager.startUpdatingLocation()
        except Exception:
            pass
    except Exception:
        if on_result:
            on_result(None)


# ======================================================================
# Android implementation: LocationListener
# ======================================================================


def _android_get(on_result: Optional[Callable], **options: Any) -> None:
    try:
        from java import dynamic_proxy, jclass

        from ..utils import get_android_context

        ctx = get_android_context()
        Context = jclass("android.content.Context")
        lm = ctx.getSystemService(Context.LOCATION_SERVICE)

        # Try the most recent known fix first — it's instant and avoids
        # the GPS warm-up delay. If unavailable or stale, fall back to
        # registering a listener for a fresh fix.
        try:
            for provider in ("gps", "network", "passive"):
                loc = lm.getLastKnownLocation(provider)
                if loc is not None:
                    if on_result is not None:
                        on_result((float(loc.getLatitude()), float(loc.getLongitude())))
                    return
        except Exception:
            pass

        LocationListener = jclass("android.location.LocationListener")

        delivered = [False]

        class _PNLocationListener(dynamic_proxy(LocationListener)):  # type: ignore[misc]
            def onLocationChanged(self, loc: Any) -> None:
                if delivered[0]:
                    return
                delivered[0] = True
                try:
                    lm.removeUpdates(self)
                except Exception:
                    pass
                if on_result is not None:
                    try:
                        on_result((float(loc.getLatitude()), float(loc.getLongitude())))
                    except Exception:
                        pass

            def onStatusChanged(self, provider: Any, status: int, extras: Any) -> None:
                pass

            def onProviderEnabled(self, provider: Any) -> None:
                pass

            def onProviderDisabled(self, provider: Any) -> None:
                if delivered[0]:
                    return
                delivered[0] = True
                try:
                    lm.removeUpdates(self)
                except Exception:
                    pass
                if on_result is not None:
                    try:
                        on_result(None)
                    except Exception:
                        pass

        listener = _PNLocationListener()
        _pending_delegates[id(listener)] = listener
        try:
            lm.requestSingleUpdate("gps", listener, None)
        except Exception:
            try:
                lm.requestLocationUpdates(
                    "network",
                    1000,
                    0.0,
                    listener,
                )
            except Exception:
                if on_result is not None:
                    on_result(None)
    except Exception:
        if on_result:
            on_result(None)
