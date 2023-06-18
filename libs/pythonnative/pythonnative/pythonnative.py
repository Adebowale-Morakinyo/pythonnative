# Detect the platform
import platform

system: str = platform.system()


class PlatformNotDetectedError(Exception):
    pass


# Depending on the system, import appropriate classes
if system == "iOS":
    from rubicon.objc import ObjCClass

    class Screen:
        native_class = ObjCClass("UIViewController")

        def __init__(self):
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

    class Button:
        native_class = ObjCClass("UIButton")

        def __init__(self, title: str = "") -> None:
            self.native_instance = self.native_class.alloc().init()
            self.set_title(title)

        def set_title(self, title: str) -> None:
            self.native_instance.setTitle_forState_(title, 0)

        def get_title(self) -> str:
            return self.native_instance.titleForState_(0)

    class Label:
        native_class = ObjCClass("UILabel")

        def __init__(self, text: str = "") -> None:
            self.native_instance = self.native_class.alloc().init()
            self.set_text(text)

        def set_text(self, text: str) -> None:
            self.native_instance.setText_(text)

        def get_text(self) -> str:
            return self.native_instance.text()

    class LinearLayout:
        native_class = ObjCClass("UIStackView")

        def __init__(self) -> None:
            self.native_instance = self.native_class.alloc().initWithFrame_(
                ((0, 0), (0, 0))
            )
            self.native_instance.setAxis_(0)  # Set axis to vertical
            self.views = []

        def add_view(self, view):
            self.views.append(view)
            self.native_instance.addArrangedSubview_(view.native_instance)

elif system == "Android":
    from java import jclass

    class Screen:
        native_class = jclass("android.app.Activity")

        def __init__(self):
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

    class Button:
        native_class = jclass("android.widget.Button")

        def __init__(self, title: str = "") -> None:
            self.native_instance = self.native_class()
            self.set_title(title)

        def set_title(self, title: str) -> None:
            self.native_instance.setText(title)

        def get_title(self) -> str:
            return self.native_instance.getText().toString()

    class Label:
        native_class = jclass("android.widget.TextView")

        def __init__(self, text: str = "") -> None:
            self.native_instance = self.native_class()
            self.set_text(text)

        def set_text(self, text: str) -> None:
            self.native_instance.setText(text)

        def get_text(self) -> str:
            return self.native_instance.getText().toString()

    class LinearLayout:
        native_class = jclass("android.widget.LinearLayout")

        def __init__(self) -> None:
            self.native_instance = self.native_class()
            self.native_instance.setOrientation(1)  # Set orientation to vertical
            self.views = []

        def add_view(self, view):
            self.views.append(view)
            self.native_instance.addView(view.native_instance)

else:
    raise PlatformNotDetectedError("Platform could not be detected or is unsupported.")
