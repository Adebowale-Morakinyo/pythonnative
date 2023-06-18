import platform
from .view import View

if platform.system() == "Android":
    from java import jclass

    class Button(View):
        native_class = jclass("android.widget.Button")

        def __init__(self, title: str = "") -> None:
            super().__init__()
            self.native_instance = self.native_class()
            self.set_title(title)

        def set_title(self, title: str) -> None:
            self.native_instance.setText(title)

        def get_title(self) -> str:
            return self.native_instance.getText().toString()

elif platform.system() == "iOS":
    from rubicon.objc import ObjCClass

    class Button(View):
        native_class = ObjCClass("UIButton")

        def __init__(self, title: str = "") -> None:
            super().__init__()
            self.native_instance = self.native_class.alloc().init()
            self.set_title(title)

        def set_title(self, title: str) -> None:
            self.native_instance.setTitle_forState_(title, 0)

        def get_title(self) -> str:
            return self.native_instance.titleForState_(0)
