from abc import ABC
from typing import Any, Optional, Tuple

# ========================================
# Base class
# ========================================


class ViewBase(ABC):
    def __init__(self) -> None:
        # Native bridge handles return types dynamically; these attributes are set at runtime.
        self.native_instance: Any = None
        self.native_class: Any = None
        # Record margins for parents that can apply them (Android LinearLayout)
        self._pn_margin: Optional[Tuple[int, int, int, int]] = None

    # ========================================
    # Lightweight style helpers
    # ========================================

    def set_background_color(self, color: Any) -> "ViewBase":
        """Set background color. Accepts platform color int or CSS-like hex string. Returns self."""
        try:
            from .utils import IS_ANDROID

            if isinstance(color, str):
                # Support formats: #RRGGBB or #AARRGGBB
                c = color.strip()
                if c.startswith("#"):
                    c = c[1:]
                if len(c) == 6:
                    c = "FF" + c
                color_int = int(c, 16)
            else:
                color_int = int(color)

            if IS_ANDROID:
                # Android expects ARGB int
                self.native_instance.setBackgroundColor(color_int)
            else:
                # iOS expects a UIColor
                from rubicon.objc import ObjCClass

                UIColor = ObjCClass("UIColor")
                a = ((color_int >> 24) & 0xFF) / 255.0
                r = ((color_int >> 16) & 0xFF) / 255.0
                g = ((color_int >> 8) & 0xFF) / 255.0
                b = (color_int & 0xFF) / 255.0
                try:
                    color_obj = UIColor.colorWithRed_green_blue_alpha_(r, g, b, a)
                except Exception:
                    color_obj = UIColor.blackColor()
                try:
                    self.native_instance.setBackgroundColor_(color_obj)
                except Exception:
                    try:
                        # Some UIKit classes expose 'backgroundColor' property
                        self.native_instance.setBackgroundColor_(color_obj)
                    except Exception:
                        pass
        except Exception:
            pass
        return self

    def set_padding(
        self,
        left: Optional[int] = None,
        top: Optional[int] = None,
        right: Optional[int] = None,
        bottom: Optional[int] = None,
        all: Optional[int] = None,
        horizontal: Optional[int] = None,
        vertical: Optional[int] = None,
    ) -> "ViewBase":
        """Set padding (dp on Android; best-effort on iOS where supported). Returns self.

        When provided, 'all' applies to all sides; 'horizontal' applies to left and right;
        'vertical' applies to top and bottom; individual overrides take precedence.
        """
        try:
            from .utils import IS_ANDROID, get_android_context

            left_value = left
            top_value = top
            right_value = right
            bottom_value = bottom
            if all is not None:
                left_value = top_value = right_value = bottom_value = all
            if horizontal is not None:
                left_value = horizontal if left_value is None else left_value
                right_value = horizontal if right_value is None else right_value
            if vertical is not None:
                top_value = vertical if top_value is None else top_value
                bottom_value = vertical if bottom_value is None else bottom_value
            left_value = left_value or 0
            top_value = top_value or 0
            right_value = right_value or 0
            bottom_value = bottom_value or 0

            if IS_ANDROID:
                density = get_android_context().getResources().getDisplayMetrics().density
                lpx = int(left_value * density)
                tpx = int(top_value * density)
                rpx = int(right_value * density)
                bpx = int(bottom_value * density)
                self.native_instance.setPadding(lpx, tpx, rpx, bpx)
            else:
                # Best-effort: many UIKit views don't have direct padding; leave to containers (e.g. UIStackView)
                # No-op by default.
                pass
        except Exception:
            pass
        return self

    def set_margin(
        self,
        left: Optional[int] = None,
        top: Optional[int] = None,
        right: Optional[int] = None,
        bottom: Optional[int] = None,
        all: Optional[int] = None,
        horizontal: Optional[int] = None,
        vertical: Optional[int] = None,
    ) -> "ViewBase":
        """Record margins for this view (applied where supported). Returns self.

        Currently applied automatically when added to Android LinearLayout (StackView).
        """
        try:
            left_value = left
            top_value = top
            right_value = right
            bottom_value = bottom
            if all is not None:
                left_value = top_value = right_value = bottom_value = all
            if horizontal is not None:
                left_value = horizontal if left_value is None else left_value
                right_value = horizontal if right_value is None else right_value
            if vertical is not None:
                top_value = vertical if top_value is None else top_value
                bottom_value = vertical if bottom_value is None else bottom_value
            left_value = int(left_value or 0)
            top_value = int(top_value or 0)
            right_value = int(right_value or 0)
            bottom_value = int(bottom_value or 0)
            self._pn_margin = (left_value, top_value, right_value, bottom_value)
        except Exception:
            pass
        return self

    def wrap_in_scroll(self) -> Any:
        """Return a ScrollView containing this view as its only child. Returns the ScrollView."""
        try:
            # Local import to avoid circulars
            from .scroll_view import ScrollView

            sv = ScrollView()
            sv.add_view(self)
            return sv
        except Exception:
            return None

    # @abstractmethod
    # def add_view(self, view):
    #     pass
    #
    # @abstractmethod
    # def set_layout(self, layout):
    #     pass
    #
    # @abstractmethod
    # def show(self):
    #     pass
