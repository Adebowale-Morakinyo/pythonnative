# import pythonnative as pn
#
# button = pn.Button()
# label = pn.Label()

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

    class Label:
        native_class = ObjCClass("UILabel")

    # Add more mappings here as required...

elif system == "Android":
    from java import jclass

    # Map native Android classes to PythonNative classes
    class Button:
        native_class = jclass("android.widget.Button")

    class Label:
        native_class = jclass("android.widget.TextView")

    # Add more mappings here as required...

else:
    raise PlatformNotDetectedError("Platform could not be detected or is unsupported.")
