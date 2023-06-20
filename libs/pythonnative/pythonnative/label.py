from .utils import IS_ANDROID
from .view import View

if IS_ANDROID:
    from java import jclass

    class Label(View):
        native_class = jclass("android.widget.TextView")

        def __init__(self, context, text: str = "") -> None:
            super().__init__()
            self.native_instance = self.native_class(context)
            self.set_text(text)

        def set_text(self, text: str) -> None:
            self.native_instance.setText(text)

        def get_text(self) -> str:
            return self.native_instance.getText().toString()

else:
    from rubicon.objc import ObjCClass

    class Label(View):
        native_class = ObjCClass("UILabel")

        def __init__(self, text: str = "") -> None:
            super().__init__()
            self.native_instance = self.native_class.alloc().init()
            self.set_text(text)

        def set_text(self, text: str) -> None:
            self.native_instance.setText_(text)

        def get_text(self) -> str:
            return self.native_instance.text()
