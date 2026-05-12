"""Plugin: ship a custom native widget through the SDK.

Tweet options:
1. Ship your own native widget through the PythonNative SDK—here, a custom iOS badge. #PythonNative
2. Wrap any platform view as a reusable Python component with the native SDK. #iOS
3. A custom native badge, built once in the SDK and used like any other element. #PythonNative
"""

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from rubicon.objc import ObjCClass

import pythonnative as pn
from pythonnative.sdk import Props, ViewHandler, element_factory, native_component


@dataclass(frozen=True)
class BadgeProps(Props):
    text: str = ""
    color: str = "#0A84FF"


@native_component("Badge", props=BadgeProps, platforms=("ios",))
class IOSBadge(ViewHandler):
    """UILabel inside a coloured pill. Pair with a TextView +
    GradientDrawable handler on Android for cross-platform.
    """

    def create(self, props: Dict[str, Any]) -> Any:
        label = ObjCClass("UILabel").alloc().init()
        label.textAlignment = 1  # NSTextAlignmentCenter
        label.textColor = ObjCClass("UIColor").whiteColor
        label.layer.cornerRadius = 12
        label.layer.masksToBounds = True
        label.setTranslatesAutoresizingMaskIntoConstraints_(True)
        self.update(label, props)
        return label

    def update(self, label: Any, changed: Dict[str, Any]) -> None:
        if "text" in changed:
            label.text = f"  {changed['text']}  "
        if "color" in changed:
            hex_ = changed["color"].lstrip("#")
            r, g, b = (int(hex_[i : i + 2], 16) / 255 for i in (0, 2, 4))
            label.backgroundColor = ObjCClass("UIColor").colorWithRed_green_blue_alpha_(r, g, b, 1)

    def set_frame(self, label: Any, x: float, y: float, w: float, h: float) -> None:
        label.setFrame_(((x, y), (max(0.0, w), max(0.0, h))))

    def measure_intrinsic(self, label: Any, max_w: float, max_h: float) -> Tuple[float, float]:
        s = label.sizeThatFits_((max_w, max_h))
        return (float(s.width), float(s.height))


Badge = element_factory("Badge")


@pn.component
def App() -> pn.Element:
    return pn.Column(
        pn.Text("Inbox", style=pn.style(font_size=32, font_weight="700")),
        Badge(text="3 new"),
        style=pn.style(spacing=16, padding=24, align_items="center"),
    )
