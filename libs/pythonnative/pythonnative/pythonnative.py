# Detect the platform
import platform

system = platform.system()


class PlatformNotDetectedError(Exception):
    pass


# Depending on the system, import appropriate classes
if system == "iOS":
    from rubicon.objc import ObjCClass

    # Map native iOS classes to PythonNative classes
    class Button:
        native_class = ObjCClass("UIButton")

        def __init__(self, title=""):
            self.native_instance = self.native_class.alloc().init()
            self.set_title(title)

        def set_title(self, title):
            self.native_instance.setTitle_forState_(title, 0)  # 0 is the state for 'normal'

        def get_title(self):
            return self.native_instance.titleForState_(0)

    class Label:
        native_class = ObjCClass("UILabel")

        def __init__(self, text=""):
            self.native_instance = self.native_class.alloc().init()
            self.set_text(text)

        def set_text(self, text):
            self.native_instance.setText_(text)

        def get_text(self):
            return self.native_instance.text()

elif system == "Android":
    from java import jclass

    # Map native Android classes to PythonNative classes
    class Button:
        native_class = jclass("android.widget.Button")

        def __init__(self, title=""):
            self.native_instance = self.native_class()  # Instantiate the Java class
            self.set_title(title)

        def set_title(self, title):
            self.native_instance.setText(title)

        def get_title(self):
            return self.native_instance.getText().toString()

    class Label:
        native_class = jclass("android.widget.TextView")

        def __init__(self, text=""):
            self.native_instance = self.native_class()  # Instantiate the Java class
            self.set_text(text)

        def set_text(self, text):
            self.native_instance.setText(text)

        def get_text(self):
            return self.native_instance.getText().toString()

else:
    raise PlatformNotDetectedError("Platform could not be detected or is unsupported.")
