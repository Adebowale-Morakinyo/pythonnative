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

    @abstractmethod
    def on_create(self):
        pass

    @abstractmethod
    def on_start(self):
        pass

    @abstractmethod
    def on_resume(self):
        pass

    @abstractmethod
    def on_pause(self):
        pass

    @abstractmethod
    def on_stop(self):
        pass

    @abstractmethod
    def on_destroy(self):
        pass

    @abstractmethod
    def on_restart(self):
        pass

    @abstractmethod
    def on_save_instance_state(self):
        pass

    @abstractmethod
    def on_restore_instance_state(self):
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
            # self.native_instance = self.native_class()

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

        def on_create(self):
            print("Android on_create() called")

        def on_start(self):
            print("Android on_start() called")

        def on_resume(self):
            print("Android on_resume() called")

        def on_pause(self):
            print("Android on_pause() called")

        def on_stop(self):
            print("Android on_stop() called")

        def on_destroy(self):
            print("Android on_destroy() called")

        def on_restart(self):
            print("Android on_restart() called")

        def on_save_instance_state(self):
            print("Android on_save_instance_state() called")

        def on_restore_instance_state(self):
            print("Android on_restore_instance_state() called")

else:
    # ========================================
    # iOS class
    # ========================================

    from rubicon.objc import ObjCClass

    class Page(PageBase, ViewBase):
        def __init__(self):
            super().__init__()
            self.native_class = ObjCClass("UIViewController")
            # self.native_instance = self.native_class.alloc().init()

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

        def on_create(self):
            print("iOS on_create() called")

        def on_start(self):
            print("iOS on_start() called")

        def on_resume(self):
            print("iOS on_resume() called")

        def on_pause(self):
            print("iOS on_pause() called")

        def on_stop(self):
            print("iOS on_stop() called")

        def on_destroy(self):
            print("iOS on_destroy() called")

        def on_restart(self):
            print("iOS on_restart() called")

        def on_save_instance_state(self):
            print("iOS on_save_instance_state() called")

        def on_restore_instance_state(self):
            print("iOS on_restore_instance_state() called")
