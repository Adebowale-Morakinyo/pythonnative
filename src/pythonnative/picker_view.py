from abc import ABC, abstractmethod

from .utils import IS_ANDROID
from .view import ViewBase

# ========================================
# Base class
# ========================================


class PickerViewBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def set_selected(self, index: int) -> "PickerViewBase":
        pass

    @abstractmethod
    def get_selected(self) -> int:
        pass


if IS_ANDROID:
    # ========================================
    # Android class
    # https://developer.android.com/reference/android/widget/Spinner
    # ========================================

    from typing import Any

    from java import jclass

    class PickerView(PickerViewBase, ViewBase):
        def __init__(self, context: Any, index: int = 0) -> None:
            super().__init__()
            self.native_class = jclass("android.widget.Spinner")
            self.native_instance = self.native_class(context)
            self.set_selected(index)

        def set_selected(self, index: int) -> "PickerView":
            self.native_instance.setSelection(index)
            return self

        def get_selected(self) -> int:
            return self.native_instance.getSelectedItemPosition()

else:
    # ========================================
    # iOS class
    # https://developer.apple.com/documentation/uikit/uipickerview
    # ========================================

    from rubicon.objc import ObjCClass

    class PickerView(PickerViewBase, ViewBase):
        def __init__(self, index: int = 0) -> None:
            super().__init__()
            self.native_class = ObjCClass("UIPickerView")
            self.native_instance = self.native_class.alloc().init()
            self.set_selected(index)

        def set_selected(self, index: int) -> "PickerView":
            self.native_instance.selectRow_inComponent_animated_(index, 0, False)
            return self

        def get_selected(self) -> int:
            return self.native_instance.selectedRowInComponent_(0)
