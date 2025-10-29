from abc import ABC, abstractmethod
from typing import Any, List

from .utils import IS_ANDROID, get_android_context
from .view import ViewBase

# ========================================
# Base class
# ========================================


class StackViewBase(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self.views: List[Any] = []

    @abstractmethod
    def add_view(self, view) -> None:
        pass

    @abstractmethod
    def set_axis(self, axis: str):
        pass

    @abstractmethod
    def set_spacing(self, spacing):
        pass

    @abstractmethod
    def set_alignment(self, alignment: str):
        pass


if IS_ANDROID:
    # ========================================
    # Android class
    # https://developer.android.com/reference/android/widget/LinearLayout
    # ========================================

    from java import jclass

    class StackView(StackViewBase, ViewBase):
        def __init__(self) -> None:
            super().__init__()
            self.native_class = jclass("android.widget.LinearLayout")
            context = get_android_context()
            self.native_instance = self.native_class(context)
            self.native_instance.setOrientation(self.native_class.VERTICAL)
            # Cache context and current orientation for spacing/alignment helpers
            self._context = context
            self._axis = "vertical"

        def add_view(self, view):
            self.views.append(view)
            # Apply margins if the child has any recorded (supported for LinearLayout)
            try:
                lp = view.native_instance.getLayoutParams()
            except Exception:
                lp = None
            if lp is None:
                # Create default LayoutParams (WRAP_CONTENT)
                layout_params = jclass("android.widget.LinearLayout$LayoutParams")(-2, -2)
            else:
                layout_params = lp
            margin = getattr(view, "_pn_margin", None)
            if margin is not None:
                left, top, right, bottom = margin
                # Convert dp to px
                density = self._context.getResources().getDisplayMetrics().density
                lpx = int(left * density)
                tpx = int(top * density)
                rpx = int(right * density)
                bpx = int(bottom * density)
                try:
                    layout_params.setMargins(lpx, tpx, rpx, bpx)
                except Exception:
                    pass
            try:
                view.native_instance.setLayoutParams(layout_params)
            except Exception:
                pass
            self.native_instance.addView(view.native_instance)

        def set_axis(self, axis: str):
            """Set stacking axis: 'vertical' or 'horizontal'. Returns self."""
            axis_l = (axis or "").lower()
            if axis_l not in ("vertical", "horizontal"):
                return self
            orientation = self.native_class.VERTICAL if axis_l == "vertical" else self.native_class.HORIZONTAL
            self.native_instance.setOrientation(orientation)
            self._axis = axis_l
            return self

        def set_spacing(self, spacing_dp: int):
            """Set spacing between children in dp (Android: uses LinearLayout dividers). Returns self."""
            try:
                density = self._context.getResources().getDisplayMetrics().density
                px = max(0, int(spacing_dp * density))
                # Use a transparent GradientDrawable with specified size as divider
                GradientDrawable = jclass("android.graphics.drawable.GradientDrawable")
                drawable = GradientDrawable()
                drawable.setColor(0x00000000)
                if self._axis == "vertical":
                    drawable.setSize(1, px)
                else:
                    drawable.setSize(px, 1)
                self.native_instance.setShowDividers(self.native_class.SHOW_DIVIDER_MIDDLE)
                self.native_instance.setDividerDrawable(drawable)
            except Exception:
                pass
            return self

        def set_alignment(self, alignment: str):
            """Set cross-axis alignment: 'fill', 'center', 'leading'/'top', 'trailing'/'bottom'. Returns self."""
            try:
                Gravity = jclass("android.view.Gravity")
                a = (alignment or "").lower()
                if self._axis == "vertical":
                    # Cross-axis is horizontal
                    if a in ("fill",):
                        self.native_instance.setGravity(Gravity.FILL_HORIZONTAL)
                    elif a in ("center", "centre"):
                        self.native_instance.setGravity(Gravity.CENTER_HORIZONTAL)
                    elif a in ("leading", "start", "left"):
                        self.native_instance.setGravity(Gravity.START)
                    elif a in ("trailing", "end", "right"):
                        self.native_instance.setGravity(Gravity.END)
                else:
                    # Cross-axis is vertical
                    if a in ("fill",):
                        self.native_instance.setGravity(Gravity.FILL_VERTICAL)
                    elif a in ("center", "centre"):
                        self.native_instance.setGravity(Gravity.CENTER_VERTICAL)
                    elif a in ("top",):
                        self.native_instance.setGravity(Gravity.TOP)
                    elif a in ("bottom",):
                        self.native_instance.setGravity(Gravity.BOTTOM)
            except Exception:
                pass
            return self

else:
    # ========================================
    # iOS class
    # https://developer.apple.com/documentation/uikit/uistackview
    # ========================================

    from rubicon.objc import ObjCClass

    class StackView(StackViewBase, ViewBase):
        def __init__(self) -> None:
            super().__init__()
            self.native_class = ObjCClass("UIStackView")
            self.native_instance = self.native_class.alloc().initWithFrame_(((0, 0), (0, 0)))
            # Default to vertical axis
            self.native_instance.setAxis_(1)

        def add_view(self, view):
            self.views.append(view)
            self.native_instance.addArrangedSubview_(view.native_instance)

        def set_axis(self, axis: str):
            """Set stacking axis: 'vertical' or 'horizontal'. Returns self."""
            axis_l = (axis or "").lower()
            value = 1 if axis_l == "vertical" else 0
            try:
                self.native_instance.setAxis_(value)
            except Exception:
                pass
            return self

        def set_spacing(self, spacing: float):
            """Set spacing between arranged subviews. Returns self."""
            try:
                self.native_instance.setSpacing_(float(spacing))
            except Exception:
                pass
            return self

        def set_alignment(self, alignment: str):
            """Set cross-axis alignment: 'fill', 'center', 'leading'/'top', 'trailing'/'bottom'. Returns self."""
            a = (alignment or "").lower()
            # UIStackViewAlignment: Fill=0, Leading/Top=1, Center=3, Trailing/Bottom=4
            mapping = {
                "fill": 0,
                "leading": 1,
                "top": 1,
                "center": 3,
                "centre": 3,
                "trailing": 4,
                "bottom": 4,
            }
            value = mapping.get(a, 0)
            try:
                self.native_instance.setAlignment_(value)
            except Exception:
                pass
            return self
