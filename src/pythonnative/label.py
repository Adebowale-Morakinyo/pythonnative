from abc import ABC, abstractmethod
from typing import Any

from .utils import IS_ANDROID, get_android_context
from .view import ViewBase

# ========================================
# Base class
# ========================================


class LabelBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def set_text(self, text: str) -> "LabelBase":
        pass

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def set_text_color(self, color: Any) -> "LabelBase":
        pass

    @abstractmethod
    def set_text_size(self, size: float) -> "LabelBase":
        pass


if IS_ANDROID:
    # ========================================
    # Android class
    # https://developer.android.com/reference/android/widget/TextView
    # ========================================

    from java import jclass

    class Label(LabelBase, ViewBase):
        def __init__(self, text: str = "") -> None:
            super().__init__()
            self.native_class = jclass("android.widget.TextView")
            context = get_android_context()
            self.native_instance = self.native_class(context)
            self.set_text(text)

        def set_text(self, text: str) -> "Label":
            self.native_instance.setText(text)
            return self

        def get_text(self) -> str:
            return self.native_instance.getText().toString()

        def set_text_color(self, color: Any) -> "Label":
            # Accept int ARGB or hex string
            if isinstance(color, str):
                c = color.strip()
                if c.startswith("#"):
                    c = c[1:]
                if len(c) == 6:
                    c = "FF" + c
                color_int = int(c, 16)
            else:
                color_int = int(color)
            try:
                self.native_instance.setTextColor(color_int)
            except Exception:
                pass
            return self

        def set_text_size(self, size_sp: float) -> "Label":
            try:
                self.native_instance.setTextSize(float(size_sp))
            except Exception:
                pass
            return self

else:
    # ========================================
    # iOS class
    # https://developer.apple.com/documentation/uikit/uilabel
    # ========================================

    from rubicon.objc import ObjCClass

    class Label(LabelBase, ViewBase):
        def __init__(self, text: str = "") -> None:
            super().__init__()
            self.native_class = ObjCClass("UILabel")
            self.native_instance = self.native_class.alloc().init()
            self.set_text(text)

        def set_text(self, text: str) -> "Label":
            self.native_instance.setText_(text)
            return self

        def get_text(self) -> str:
            return self.native_instance.text()

        def set_text_color(self, color: Any) -> "Label":
            # Accept int ARGB or hex string
            if isinstance(color, str):
                c = color.strip()
                if c.startswith("#"):
                    c = c[1:]
                if len(c) == 6:
                    c = "FF" + c
                color_int = int(c, 16)
            else:
                color_int = int(color)
            try:
                UIColor = ObjCClass("UIColor")
                a = ((color_int >> 24) & 0xFF) / 255.0
                r = ((color_int >> 16) & 0xFF) / 255.0
                g = ((color_int >> 8) & 0xFF) / 255.0
                b = (color_int & 0xFF) / 255.0
                color_obj = UIColor.colorWithRed_green_blue_alpha_(r, g, b, a)
                self.native_instance.setTextColor_(color_obj)
            except Exception:
                pass
            return self

        def set_text_size(self, size: float) -> "Label":
            try:
                UIFont = ObjCClass("UIFont")
                font = UIFont.systemFontOfSize_(float(size))
                self.native_instance.setFont_(font)
            except Exception:
                pass
            return self
