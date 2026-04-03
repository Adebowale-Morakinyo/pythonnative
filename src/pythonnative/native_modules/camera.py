"""Cross-platform camera access.

Provides methods for capturing photos and picking images from the gallery.
Uses Android's ``Intent``/``MediaStore`` or iOS's ``UIImagePickerController``.
"""

from typing import Any, Callable, Optional

from ..utils import IS_ANDROID


class Camera:
    """Camera and image picker interface.

    All methods accept an ``on_result`` callback that receives the image
    file path (or ``None`` on cancellation).
    """

    @staticmethod
    def take_photo(on_result: Optional[Callable[[Optional[str]], None]] = None, **options: Any) -> None:
        """Launch the device camera to capture a photo.

        Parameters
        ----------
        on_result:
            ``(path_or_none) -> None`` called with the saved image path,
            or ``None`` if the user cancelled.
        """
        if IS_ANDROID:
            Camera._android_take_photo(on_result, **options)
        else:
            Camera._ios_take_photo(on_result, **options)

    @staticmethod
    def pick_from_gallery(on_result: Optional[Callable[[Optional[str]], None]] = None, **options: Any) -> None:
        """Open the system gallery picker.

        Parameters
        ----------
        on_result:
            ``(path_or_none) -> None`` called with the selected image path,
            or ``None`` if the user cancelled.
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
