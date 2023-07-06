from abc import ABC, abstractmethod
from .utils import IS_ANDROID
from .view import ViewBase

# ========================================
# Base class
# ========================================


class MaterialButtonBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def set_title(self, title: str) -> None:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass


if IS_ANDROID:
    # ========================================
    # Android class
    # ========================================

    from java import jclass

    class MaterialButton(MaterialButtonBase, ViewBase):
        def __init__(self, context, title: str = "") -> None:
            super().__init__()
            self.native_class = jclass(
                "com.google.android.material.button.MaterialButton"
            )
            self.native_instance = self.native_class(context)
            self.set_title(title)

        def set_title(self, title: str) -> None:
            self.native_instance.setText(title)

        def get_title(self) -> str:
            return self.native_instance.getText().toString()

else:
    # ========================================
    # iOS class
    # ========================================

    from rubicon.objc import ObjCClass

    class MaterialButton(MaterialButtonBase, ViewBase):
        def __init__(self, title: str = "") -> None:
            super().__init__()
            self.native_class = ObjCClass(
                "UIButton"
            )  # Apple does not have a direct equivalent for MaterialButton
            self.native_instance = self.native_class.alloc().init()
            self.set_title(title)

        def set_title(self, title: str) -> None:
            self.native_instance.setTitle_forState_(title, 0)

        def get_title(self) -> str:
            return self.native_instance.titleForState_(0)
