"""Cross-platform camera and gallery access.

Provides static methods for capturing a photo or picking an image from
the device gallery. The platform implementation is selected at call
time and uses Android's `Intent`/`MediaStore` APIs or iOS's
`UIImagePickerController`.

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

from typing import Any, Callable, Optional

from ..utils import IS_ANDROID


class Camera:
    """Camera and image-picker interface.

    All methods are static. They dispatch to the Android or iOS
    implementation at call time based on `IS_ANDROID` (from
    `pythonnative.utils`).
    """

    @staticmethod
    def take_photo(on_result: Optional[Callable[[Optional[str]], None]] = None, **options: Any) -> None:
        """Launch the device camera to capture a photo.

        Args:
            on_result: Callable invoked with the saved image path, or
                `None` if the user cancelled.
            **options: Reserved for platform-specific tuning. Currently
                unused; future kwargs (e.g., `quality`, `flash_mode`)
                will land here.
        """
        if IS_ANDROID:
            Camera._android_take_photo(on_result, **options)
        else:
            Camera._ios_take_photo(on_result, **options)

    @staticmethod
    def pick_from_gallery(on_result: Optional[Callable[[Optional[str]], None]] = None, **options: Any) -> None:
        """Open the system gallery picker.

        Args:
            on_result: Callable invoked with the selected image path, or
                `None` if the user cancelled.
            **options: Reserved for platform-specific tuning.
        """
        if IS_ANDROID:
            Camera._android_pick_gallery(on_result, **options)
        else:
            Camera._ios_pick_gallery(on_result, **options)

    # -- Android implementations -----------------------------------------

    @staticmethod
    def _android_take_photo(on_result: Optional[Callable] = None, **options: Any) -> None:
        try:
            from java import jclass

            Intent = jclass("android.content.Intent")
            MediaStore = jclass("android.provider.MediaStore")
            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            from ..utils import get_android_context

            ctx = get_android_context()
            ctx.startActivity(intent)
        except Exception:
            if on_result:
                on_result(None)

    @staticmethod
    def _android_pick_gallery(on_result: Optional[Callable] = None, **options: Any) -> None:
        try:
            from java import jclass

            Intent = jclass("android.content.Intent")
            intent = Intent(Intent.ACTION_PICK)
            intent.setType("image/*")
            from ..utils import get_android_context

            ctx = get_android_context()
            ctx.startActivity(intent)
        except Exception:
            if on_result:
                on_result(None)

    # -- iOS implementations ---------------------------------------------

    @staticmethod
    def _ios_take_photo(on_result: Optional[Callable] = None, **options: Any) -> None:
        try:
            from rubicon.objc import ObjCClass

            picker = ObjCClass("UIImagePickerController").alloc().init()
            picker.setSourceType_(1)  # UIImagePickerControllerSourceTypeCamera
        except Exception:
            if on_result:
                on_result(None)

    @staticmethod
    def _ios_pick_gallery(on_result: Optional[Callable] = None, **options: Any) -> None:
        try:
            from rubicon.objc import ObjCClass

            picker = ObjCClass("UIImagePickerController").alloc().init()
            picker.setSourceType_(0)  # PhotoLibrary
        except Exception:
            if on_result:
                on_result(None)
