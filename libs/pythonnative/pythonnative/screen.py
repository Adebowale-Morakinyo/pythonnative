from .utils import IS_ANDROID
from .view import View

if IS_ANDROID:
    from java import jclass

    class Screen(View):
        native_class = jclass("android.app.Activity")

        def __init__(self):
            super().__init__()
            self.native_instance = self.native_class()
            self.layout = None

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
    from rubicon.objc import ObjCClass

    class Screen(View):
        native_class = ObjCClass("UIViewController")

        def __init__(self):
            super().__init__()
            self.native_instance = self.native_class.alloc().init()
            self.layout = None

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
