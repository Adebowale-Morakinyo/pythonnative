from .utils import IS_ANDROID
from .view import View

if IS_ANDROID:
    from java import jclass

    class Button(View):
        def __init__(self, context, title: str = "") -> None:
            super().__init__()
            self.native_class = jclass("android.widget.Button")
            self.native_instance = self.native_class(context)
            self.set_title(title)

        def set_title(self, title: str) -> None:
            self.native_instance.setText(title)

        def get_title(self) -> str:
            return self.native_instance.getText().toString()

else:
    from rubicon.objc import ObjCClass

    class Button(View):
        def __init__(self, title: str = "") -> None:
            super().__init__()
            self.native_class = ObjCClass("UIButton")
            self.native_instance = self.native_class.alloc().init()
            self.set_title(title)

        def set_title(self, title: str) -> None:
            self.native_instance.setTitle_forState_(title, 0)

        def get_title(self) -> str:
            return self.native_instance.titleForState_(0)
