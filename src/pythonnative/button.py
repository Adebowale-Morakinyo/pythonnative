from abc import ABC, abstractmethod
from typing import Callable
from .utils import IS_ANDROID
from .view import ViewBase

# ========================================
# Base class
# ========================================


class ButtonBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def set_title(self, title: str) -> None:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def set_on_click(self, callback: Callable[[], None]) -> None:
        pass


if IS_ANDROID:
    # ========================================
    # Android class
    # https://developer.android.com/reference/android/widget/Button
    # ========================================

    from java import dynamic_proxy, jclass

    class Button(ButtonBase, ViewBase):
        def __init__(self, context, title: str = "") -> None:
            super().__init__()
            self.native_class = jclass("android.widget.Button")
            self.native_instance = self.native_class(context)
            self.set_title(title)

        def set_title(self, title: str) -> None:
            self.native_instance.setText(title)

        def get_title(self) -> str:
            return self.native_instance.getText().toString()

        def set_on_click(self, callback: Callable[[], None]) -> None:
            class OnClickListener(
                dynamic_proxy(jclass("android.view.View").OnClickListener)
            ):
                def __init__(self, callback):
                    super().__init__()
                    self.callback = callback

                def onClick(self, view):
                    self.callback()

            listener = OnClickListener(callback)
            self.native_instance.setOnClickListener(listener)

else:
    # ========================================
    # iOS class
    # https://developer.apple.com/documentation/uikit/uibutton
    # ========================================

    from rubicon.objc import ObjCClass, SEL

    class Button(ButtonBase, ViewBase):
        def __init__(self, title: str = "") -> None:
            super().__init__()
            self.native_class = ObjCClass("UIButton")
            self.native_instance = self.native_class.alloc().init()
            self.set_title(title)

        def set_title(self, title: str) -> None:
            self.native_instance.setTitle_forState_(title, 0)

        def get_title(self) -> str:
            return self.native_instance.titleForState_(0)

        def set_on_click(self, callback: Callable[[], None]) -> None:
            def objc_callback(_cmd, sender):
                callback()

            action = SEL(objc_callback)
            self.native_instance.addTarget_action_forControlEvents_(
                self.native_instance, action, 1
            )
