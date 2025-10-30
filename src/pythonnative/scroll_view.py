from abc import ABC, abstractmethod
from typing import Any, List

from .utils import IS_ANDROID, get_android_context
from .view import ViewBase

# ========================================
# Base class
# ========================================


class ScrollViewBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self.views: List[Any] = []

    @abstractmethod
    def add_view(self, view: Any) -> None:
        pass

    @staticmethod
    @abstractmethod
    def wrap(view: Any) -> "ScrollViewBase":
        """Return a new ScrollView containing the provided view as its only child."""
        pass


if IS_ANDROID:
    # ========================================
    # Android class
    # https://developer.android.com/reference/android/widget/ScrollView
    # ========================================

    from java import jclass

    class ScrollView(ScrollViewBase, ViewBase):
        def __init__(self) -> None:
            super().__init__()
            self.native_class = jclass("android.widget.ScrollView")
            context = get_android_context()
            self.native_instance = self.native_class(context)

        def add_view(self, view: Any) -> None:
            self.views.append(view)
            # In Android, ScrollView can host only one direct child
            if len(self.views) == 1:
                self.native_instance.addView(view.native_instance)
            else:
                raise Exception("ScrollView can host only one direct child")

        @staticmethod
        def wrap(view: Any) -> "ScrollView":
            """Return a new ScrollView containing the provided view as its only child."""
            sv = ScrollView()
            sv.add_view(view)
            return sv

else:
    # ========================================
    # iOS class
    # https://developer.apple.com/documentation/uikit/uiscrollview
    # ========================================

    from rubicon.objc import ObjCClass

    class ScrollView(ScrollViewBase, ViewBase):
        def __init__(self) -> None:
            super().__init__()
            self.native_class = ObjCClass("UIScrollView")
            self.native_instance = self.native_class.alloc().initWithFrame_(((0, 0), (0, 0)))

        def add_view(self, view: Any) -> None:
            self.views.append(view)
            # Add as subview and size child to fill scroll view by default so content is visible
            try:
                self.native_instance.addSubview_(view.native_instance)
            except Exception:
                pass
            # Default layout: if the child has no size yet, size it to fill the scroll view
            # and enable flexible width/height. If the child is already sized explicitly,
            # leave it unchanged.
            try:
                frame = getattr(view.native_instance, "frame")
                size = getattr(frame, "size", None)
                width = getattr(size, "width", 0) if size is not None else 0
                height = getattr(size, "height", 0) if size is not None else 0
                if width <= 0 or height <= 0:
                    bounds = self.native_instance.bounds
                    view.native_instance.setFrame_(bounds)
                    # UIViewAutoresizingFlexibleWidth (2) | UIViewAutoresizingFlexibleHeight (16)
                    view.native_instance.setAutoresizingMask_(2 | 16)
            except Exception:
                pass

        @staticmethod
        def wrap(view: Any) -> "ScrollView":
            """Return a new ScrollView containing the provided view as its only child."""
            sv = ScrollView()
            sv.add_view(view)
            return sv
