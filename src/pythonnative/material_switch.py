from abc import ABC, abstractmethod

from .utils import IS_ANDROID
from .view import ViewBase

# ========================================
# Base class
# ========================================


class MaterialSwitchBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def set_on(self, value: bool) -> "MaterialSwitchBase":
        pass

    @abstractmethod
    def is_on(self) -> bool:
        pass


if IS_ANDROID:
    # ========================================
    # Android class
    # https://developer.android.com/reference/com/google/android/material/materialswitch/MaterialSwitch
    # ========================================

    from typing import Any

    from java import jclass

    class MaterialSwitch(MaterialSwitchBase, ViewBase):
        def __init__(self, context: Any, value: bool = False) -> None:
            super().__init__()
            self.native_class = jclass("com.google.android.material.switch.MaterialSwitch")
            self.native_instance = self.native_class(context)
            self.set_on(value)

        def set_on(self, value: bool) -> "MaterialSwitch":
            self.native_instance.setChecked(value)
            return self

        def is_on(self) -> bool:
            return self.native_instance.isChecked()

else:
    # ========================================
    # iOS class
    # https://developer.apple.com/documentation/uikit/uiswitch
    # ========================================

    from rubicon.objc import ObjCClass

    class MaterialSwitch(MaterialSwitchBase, ViewBase):
        def __init__(self, value: bool = False) -> None:
            super().__init__()
            self.native_class = ObjCClass("UISwitch")
            self.native_instance = self.native_class.alloc().init()
            self.set_on(value)

        def set_on(self, value: bool) -> "MaterialSwitch":
            self.native_instance.setOn_animated_(value, False)
            return self

        def is_on(self) -> bool:
            return self.native_instance.isOn()
