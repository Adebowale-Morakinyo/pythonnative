from abc import ABC, abstractmethod
from .utils import IS_ANDROID
from .view import ViewBase

# ========================================
# Base class
# ========================================


class PageBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self.layout = None

    @abstractmethod
    def add_view(self, view) -> None:
        pass

    @abstractmethod
    def set_layout(self, layout) -> None:
        pass

    @abstractmethod
    def show(self) -> None:
        pass


if IS_ANDROID:
    # ========================================
    # Android class
    # ========================================

    from java import jclass

    class Page(PageBase, ViewBase):
        def __init__(self):
            super().__init__()
            self.native_class = jclass("android.app.Activity")
            self.native_instance = self.native_class()

        def add_view(self, view):
            if self.layout is None:
                raise ValueError("You must set a layout before adding views.")
            self.layout.add_view(view)

        def set_layout(self, layout):
            self.layout = layout
            self.native_instance.setContentView(layout.native_instance)

        def show(self):
            # This method should contain code to start the Activity
            pass

else:
    # ========================================
    # iOS class
    # ========================================

    from rubicon.objc import ObjCClass

    class Page(PageBase, ViewBase):
        def __init__(self):
            super().__init__()
            self.native_class = ObjCClass("UIViewController")
            self.native_instance = self.native_class.alloc().init()

        def add_view(self, view):
            if self.layout is None:
                raise ValueError("You must set a layout before adding views.")
            self.layout.add_view(view)

        def set_layout(self, layout):
            self.layout = layout
            self.native_instance.view().addSubview_(layout.native_instance)

        def show(self):
            # This method should contain code to present the ViewController
            pass
