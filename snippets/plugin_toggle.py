"""Plugin (minimal): wrap a UISwitch through the SDK in ~30 lines.

Tweet options:
1. Wrap a native UISwitch as a Python component in about thirty lines with the SDK. #PythonNative
2. The PythonNative SDK turns a platform control into a reusable element—UISwitch included. #iOS
3. A real iOS switch, exposed to Python in roughly thirty lines of SDK code. #Python
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rubicon.objc import ObjCClass

import pythonnative as pn
from pythonnative.sdk import Props, ViewHandler, element_factory, native_component


@dataclass(frozen=True)
class ToggleProps(Props):
    on: bool = False


@native_component("Toggle", props=ToggleProps, platforms=("ios",))
class IOSToggle(ViewHandler):
    def create(self, props: dict[str, Any]) -> Any:
        sw = ObjCClass("UISwitch").alloc().init()
        sw.setOn_(bool(props.get("on", False)))
        return sw

    def update(self, sw: Any, changed: dict[str, Any]) -> None:
        if "on" in changed:
            sw.setOn_animated_(bool(changed["on"]), True)

    def set_frame(self, sw: Any, x: float, y: float, w: float, h: float) -> None:
        sw.setFrame_(((x, y), (w, h)))

    def measure_intrinsic(self, sw: Any, mw: float, mh: float) -> tuple[float, float]:
        s = sw.intrinsicContentSize()
        return (float(s.width), float(s.height))


Toggle = element_factory("Toggle")


@pn.component
def App() -> pn.Element:
    on, set_on = pn.use_state(False)
    return pn.Column(
        Toggle(on=on),
        pn.Button("Tap me", on_click=lambda: set_on(not on)),
        style=pn.style(spacing=16, padding=24, align_items="center"),
    )
