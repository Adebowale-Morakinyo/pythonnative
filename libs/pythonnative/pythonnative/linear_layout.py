from .utils import IS_ANDROID
from .view import View

if IS_ANDROID:
    from java import jclass

    class LinearLayout(View):
        native_class = jclass("android.widget.LinearLayout")

        def __init__(self, context) -> None:
            super().__init__()
            self.native_instance = self.native_class(context)
            self.native_instance.setOrientation(self.native_class.VERTICAL)  # Set orientation to vertical
            self.views = []

        def add_view(self, view):
            self.views.append(view)
            self.native_instance.addView(view.native_instance)

else:
    from rubicon.objc import ObjCClass

    class LinearLayout(View):
        native_class = ObjCClass("UIStackView")

        def __init__(self) -> None:
            super().__init__()
            self.native_instance = self.native_class.alloc().initWithFrame_(
                ((0, 0), (0, 0))
            )
            self.native_instance.setAxis_(0)  # Set axis to vertical
            self.views = []

        def add_view(self, view):
            self.views.append(view)
            self.native_instance.addArrangedSubview_(view.native_instance)
