"""Cross-platform camera and gallery access.

Provides static methods for capturing a photo or picking an image from
the device gallery. The platform implementation is selected at call
time and uses Android's `Intent`/`MediaStore` APIs (with an
`ActivityResultLauncher` for the callback) or iOS's
`UIImagePickerController` (with a strongly retained delegate that
forwards the result back to Python).

All methods accept an `on_result` callback that receives either the
saved image path (a `str`) or `None` if the user cancels.

Example:
    ```python
    from pythonnative import Camera

    def handle(path):
        print("Photo saved to" if path else "Cancelled", path)

    Camera.take_photo(on_result=handle)
    ```
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from ..utils import IS_ANDROID, IS_IOS

# Module-level retain pool so delegates aren't garbage-collected
# before the picker calls back. Keyed by id(delegate).
_pending_delegates: Dict[int, Any] = {}


class Camera:
    """Camera and image-picker interface.

    All methods are static. They dispatch to the Android or iOS
    implementation at call time based on the runtime platform
    detected in `pythonnative.utils`.
    """

    @staticmethod
    def take_photo(on_result: Optional[Callable[[Optional[str]], None]] = None, **options: Any) -> None:
        """Launch the device camera to capture a photo.

        Args:
            on_result: Callable invoked with the saved image path, or
                `None` if the user cancelled / permission was denied.
            **options: Reserved for platform-specific tuning. Currently
                unused; future kwargs (e.g., `quality`, `flash_mode`)
                will land here.
        """
        if IS_ANDROID:
            _android_launch_picker(on_result, source="camera")
        elif IS_IOS:
            _ios_launch_picker(on_result, source="camera")
        else:
            if on_result:
                on_result(None)

    @staticmethod
    def pick_from_gallery(on_result: Optional[Callable[[Optional[str]], None]] = None, **options: Any) -> None:
        """Open the system gallery picker.

        Args:
            on_result: Callable invoked with the selected image path, or
                `None` if the user cancelled.
            **options: Reserved for platform-specific tuning.
        """
        if IS_ANDROID:
            _android_launch_picker(on_result, source="gallery")
        elif IS_IOS:
            _ios_launch_picker(on_result, source="gallery")
        else:
            if on_result:
                on_result(None)


# ======================================================================
# iOS implementation: UIImagePickerControllerDelegate
# ======================================================================


def _ios_launch_picker(on_result: Optional[Callable], source: str) -> None:
    try:
        from rubicon.objc import SEL, ObjCClass, objc_method

        UIImagePickerController = ObjCClass("UIImagePickerController")
        NSObject = ObjCClass("NSObject")

        class _PNImagePickerDelegate(NSObject):  # type: ignore[misc,valid-type]
            _callback: Optional[Callable[[Optional[str]], None]] = None
            _picker: Any = None

            @objc_method
            def imagePickerController_didFinishPickingMediaWithInfo_(self, picker: Any, info: Any) -> None:
                path: Optional[str] = None
                try:
                    # Try the URL key first (works for gallery picks).
                    url = info.objectForKey_("UIImagePickerControllerImageURL")
                    if url is not None:
                        try:
                            path = str(url.absoluteString)
                        except Exception:
                            try:
                                path = str(url.path)
                            except Exception:
                                path = None
                    if path is None:
                        # Fall back to writing the UIImage to a temp file.
                        image = info.objectForKey_("UIImagePickerControllerOriginalImage")
                        if image is not None:
                            path = _ios_write_image_to_tmp(image)
                except Exception:
                    path = None

                try:
                    picker.dismissViewControllerAnimated_completion_(True, None)
                except Exception:
                    pass

                if self._callback is not None:
                    try:
                        self._callback(path)
                    except Exception:
                        pass
                _pending_delegates.pop(id(self), None)

            @objc_method
            def imagePickerControllerDidCancel_(self, picker: Any) -> None:
                try:
                    picker.dismissViewControllerAnimated_completion_(True, None)
                except Exception:
                    pass
                if self._callback is not None:
                    try:
                        self._callback(None)
                    except Exception:
                        pass
                _pending_delegates.pop(id(self), None)

        delegate = _PNImagePickerDelegate.new()
        delegate._callback = on_result
        _pending_delegates[id(delegate)] = delegate

        picker = UIImagePickerController.alloc().init()
        picker.setSourceType_(1 if source == "camera" else 0)
        picker.setDelegate_(delegate)

        # Locate the topmost VC and present.
        UIApplication = ObjCClass("UIApplication")
        top = UIApplication.sharedApplication.keyWindow.rootViewController
        while top is not None and top.presentedViewController is not None:
            top = top.presentedViewController
        if top is not None:
            top.presentViewController_animated_completion_(picker, True, None)
        # Silence the unused-import lint for SEL — it's intentionally imported
        # here to keep parity with other delegate setups even though no
        # direct selector wiring is needed (UIKit dispatches via the
        # delegate protocol).
        _ = SEL
    except Exception:
        if on_result:
            on_result(None)


def _ios_write_image_to_tmp(image: Any) -> Optional[str]:
    """Encode a UIImage to JPEG and write it to NSTemporaryDirectory."""
    try:
        from rubicon.objc import ObjCClass

        NSData = ObjCClass("NSData")  # noqa: F841
        UIImageJPEGRepresentation = ObjCClass("NSObject").class_method  # placeholder
        _ = UIImageJPEGRepresentation
        # The free function ``UIImageJPEGRepresentation`` isn't callable
        # via rubicon-objc trivially; rely on the UIImage method
        # ``jpegDataWithCompressionQuality:`` (iOS 17+) when available.
        try:
            data = image.jpegDataWithCompressionQuality_(0.85)
        except Exception:
            return None
        if data is None:
            return None
        NSString = ObjCClass("NSString")
        NSFileManager = ObjCClass("NSFileManager")
        NSTemporaryDir = ObjCClass("NSObject").alloc().init()  # placeholder
        _ = NSTemporaryDir
        # Use NSFileManager.URLForDirectory… or a fixed path under
        # the documents folder. Simplest is NSTemporaryDirectory().
        try:
            from rubicon.objc.api import objc_const  # noqa: F401
        except Exception:
            pass
        manager = NSFileManager.defaultManager
        urls = manager.URLsForDirectory_inDomains_(13, 1)  # NSCachesDirectory=13, NSUserDomainMask=1
        if urls is None or urls.count == 0:
            return None
        cache_dir = urls.firstObject
        timestamp = int(__import__("time").time() * 1000)
        filename = NSString.stringWithFormat_("pn-camera-%d.jpg", timestamp)
        target = cache_dir.URLByAppendingPathComponent_(filename)
        ok = data.writeToURL_atomically_(target, True)
        if not ok:
            return None
        try:
            return str(target.path)
        except Exception:
            return str(target.absoluteString)
    except Exception:
        return None


# ======================================================================
# Android implementation: ActivityResultLauncher / startActivityForResult
# ======================================================================


# Activity result requests are correlated by request_code; this dict
# maps request_code -> on_result callback.
_android_pending_results: Dict[int, Callable[[Optional[str]], None]] = {}
_android_next_request_code: int = 50001


def _android_next_code() -> int:
    global _android_next_request_code
    code = _android_next_request_code
    _android_next_request_code += 1
    return code


def _android_launch_picker(on_result: Optional[Callable], source: str) -> None:
    try:
        from java import jclass

        from ..utils import get_android_context

        Intent = jclass("android.content.Intent")
        MediaStore = jclass("android.provider.MediaStore")
        ctx = get_android_context()

        if source == "camera":
            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        else:
            intent = Intent(Intent.ACTION_PICK)
            intent.setType("image/*")

        # Activity is required for startActivityForResult. The page
        # host stores it via ``set_android_context`` — we look it up
        # lazily so the import works in unit-test environments where
        # there is no activity.
        Activity = jclass("android.app.Activity")
        if not Activity.isInstance(ctx):
            ctx.startActivity(intent)
            if on_result:
                on_result(None)
            return

        request_code = _android_next_code()
        if on_result is not None:
            _android_pending_results[request_code] = on_result
        try:
            ctx.startActivityForResult(intent, request_code)
        except Exception:
            _android_pending_results.pop(request_code, None)
            if on_result:
                on_result(None)
    except Exception:
        if on_result:
            on_result(None)


def deliver_android_activity_result(request_code: int, result_code: int, data: Any) -> bool:
    """Forward an Activity result to the registered camera callback.

    The host Activity should call this from `onActivityResult` so the
    pending `Camera.take_photo` / `Camera.pick_from_gallery`
    callback receives a path. Returns ``True`` if a Python callback
    was invoked (so the host can short-circuit further handlers).
    """
    cb = _android_pending_results.pop(request_code, None)
    if cb is None:
        return False
    path: Optional[str] = None
    try:
        if result_code == -1 and data is not None:  # RESULT_OK
            uri = data.getData()
            if uri is not None:
                path = str(uri)
            else:
                # Camera capture: data may carry a Bitmap thumbnail in
                # the extras; persist it to cache.
                try:
                    extras = data.getExtras()
                    if extras is not None:
                        thumb = extras.get("data")
                        if thumb is not None:
                            path = _android_write_bitmap_to_cache(thumb)
                except Exception:
                    pass
    except Exception:
        path = None
    try:
        cb(path)
    except Exception:
        pass
    return True


def _android_write_bitmap_to_cache(bitmap: Any) -> Optional[str]:
    """Persist a Bitmap to the app cache directory and return its path."""
    try:
        from java import jclass

        from ..utils import get_android_context

        ctx = get_android_context()
        cache_dir = ctx.getCacheDir()
        File = jclass("java.io.File")
        FileOutputStream = jclass("java.io.FileOutputStream")
        Bitmap = jclass("android.graphics.Bitmap")
        timestamp = int(__import__("time").time() * 1000)
        target = File(cache_dir, f"pn-camera-{timestamp}.jpg")
        out = FileOutputStream(target)
        try:
            bitmap.compress(Bitmap.CompressFormat.JPEG, 85, out)
        finally:
            out.close()
        return str(target.getAbsolutePath())
    except Exception:
        return None
