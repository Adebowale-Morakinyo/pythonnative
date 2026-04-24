# Native modules

Native modules are PythonNative's wrappers around device APIs that
aren't part of the view tree: the camera, GPS, app-scoped file I/O,
and local notifications. Each module is implemented twice (once per
platform) and dispatches at runtime based on `utils.IS_ANDROID` /
`utils.IS_IOS`, so app code stays single-source.

This guide covers the four built-in modules: where to import them,
which permissions they need, and the typical usage shape.

## Permissions: declare them once, request at runtime

PythonNative does not edit `Info.plist` or `AndroidManifest.xml` for
you. You declare what your app needs in the platform manifests, and
the operating system shows the permission prompt the first time you
call into the API.

=== "Android (`android_template/app/src/main/AndroidManifest.xml`)"

    ```xml
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    ```

=== "iOS (`ios_template/Info.plist`)"

    ```xml
    <key>NSCameraUsageDescription</key>
    <string>So you can take photos in MyApp.</string>
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>So MyApp can show nearby content.</string>
    <key>NSPhotoLibraryUsageDescription</key>
    <string>So you can pick photos from your library.</string>
    ```

The exact strings on iOS appear in the system permission dialog, so
write them as you would want a user to read them.

## Camera

[`Camera`][pythonnative.native_modules.camera.Camera] wraps photo
capture and gallery picking. Both methods return a path to the saved
file (or `None` if the user cancelled).

```python
from pythonnative.native_modules import Camera

@pn.component
def CameraScreen():
    photo, set_photo = pn.use_state(None)

    def take():
        path = Camera().take_photo()
        if path:
            set_photo(path)

    return pn.Column(
        pn.Button("Take photo", on_click=take),
        pn.Image(source=photo) if photo else pn.Spacer(),
    )
```

!!! note "Cold-start permissions"
    The first call shows the system permission prompt. If the user
    denies it, subsequent calls return `None` immediately; surface a
    helpful message in your UI rather than calling in a loop.

## Location

[`Location`][pythonnative.native_modules.location.Location] reads a
single GPS fix.

```python
from pythonnative.native_modules import Location

@pn.component
def WhereAmI():
    fix, set_fix = pn.use_state(None)

    pn.use_focus_effect(lambda: (set_fix(Location().get_current()), None)[1], deps=[])

    if fix is None:
        return pn.Text("Acquiring location...")
    return pn.Text(f"{fix['latitude']:.4f}, {fix['longitude']:.4f}")
```

For continuous updates, write a small native module that subscribes to
`CLLocationManagerDelegate` (iOS) or `LocationManager.requestUpdates`
(Android) and pushes deltas through `set_state` from the main thread.

## File system

[`FileSystem`][pythonnative.native_modules.file_system.FileSystem] is
scoped to your app's documents directory; relative paths are resolved
inside that sandbox automatically.

```python
from pythonnative.native_modules import FileSystem

fs = FileSystem()
fs.write_text("notes.txt", "hello")
fs.exists("notes.txt")           # True
fs.list_dir("")                  # ["notes.txt"]
fs.read_text("notes.txt")        # "hello"
```

For binary content, use `read_bytes` and `write_bytes`. For
sub-directories, call `ensure_dir("photos")` before writing into it.

!!! tip "Use `app_dir()` for absolute paths"
    Some native APIs (e.g., `MediaStore`, `NSFileManager`) need an
    absolute path. `fs.app_dir()` returns it without you needing to
    know the platform-specific layout.

## Notifications

[`Notifications`][pythonnative.native_modules.notifications.Notifications]
schedules local notifications and cancels previously scheduled ones.

```python
from pythonnative.native_modules import Notifications

n = Notifications()
n.request_permission()
n.schedule(id="reminder", title="Stretch break", body="Stand up!", delay_seconds=1800)
n.cancel("reminder")
```

`request_permission()` is required on iOS and on Android 13+. On older
Android, the call is a no-op.

## Writing your own native module

A native module is just a class with two implementations behind a
runtime dispatch:

```python
from pythonnative.utils import IS_ANDROID, IS_IOS

class Battery:
    def get_level(self) -> float:
        if IS_ANDROID:
            from java import jclass
            ctx = ...  # via get_android_context()
            mgr = ctx.getSystemService("batterymanager")
            return mgr.getIntProperty(jclass(...).BATTERY_PROPERTY_CAPACITY) / 100.0
        if IS_IOS:
            from rubicon.objc import ObjCClass
            UIDevice = ObjCClass("UIDevice")
            UIDevice.currentDevice.batteryMonitoringEnabled = True
            return float(UIDevice.currentDevice.batteryLevel)
        raise RuntimeError("Battery is only available on Android or iOS")
```

Keep platform imports inside the platform branch so the desktop
import path doesn't pull in Chaquopy or rubicon-objc.

## Next steps

- Reference: [Native modules API](../api/native_modules.md).
- See how device APIs interact with focus: [Lifecycle](../concepts/lifecycle.md).
- Wrap a custom widget instead of an API: [Native views](../concepts/native-views.md).
