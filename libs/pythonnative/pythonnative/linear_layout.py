from abc import ABC, abstractmethod
from .utils import IS_ANDROID
from .view import ViewBase

# ========================================
# Base class
# ========================================


class LinearLayoutBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self.views = []

    @abstractmethod
    def add_view(self, view) -> None:
        pass


if IS_ANDROID:
    # ========================================
    # Android class
    # ========================================

    from java import jclass

    class LinearLayout(LinearLayoutBase, ViewBase):
        def __init__(self, context) -> None:
            super().__init__()
            self.native_class = jclass("android.widget.LinearLayout")
            self.native_instance = self.native_class(context)
            self.native_instance.setOrientation(self.native_class.VERTICAL)

        def add_view(self, view):
            self.views.append(view)
            self.native_instance.addView(view.native_instance)

else:
    # ========================================
    # iOS class
    # ========================================

    from rubicon.objc import ObjCClass

    class LinearLayout(LinearLayoutBase, ViewBase):
        def __init__(self) -> None:
            super().__init__()
            self.native_class = ObjCClass("UIStackView")
            self.native_instance = self.native_class.alloc().initWithFrame_(
                ((0, 0), (0, 0))
            )
            self.native_instance.setAxis_(0)  # Set axis to vertical

        def add_view(self, view):
            self.views.append(view)
            self.native_instance.addArrangedSubview_(view.native_instance)
