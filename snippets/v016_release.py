"""v0.16.0: typed props, Fragment, memo, animation hooks, native Picker.

Tweet options:
1. PythonNative v0.16.0 is here: typed props, Fragment, memo, animation hooks, and a native Picker. #PythonNative
2. The v0.16.0 release brings typed props, Fragment, memo, animation hooks, and a native Picker. #Python
3. Cleaner APIs and more native controls land in PythonNative v0.16.0. #PythonNative
"""

from typing import Any

import pythonnative as pn

FEATURES: dict[str, tuple[str, str]] = {
    "props": (
        "Typed props",
        "Built-in components now have frozen Props dataclasses for clearer APIs and better editor help.",
    ),
    "fragment": (
        "Fragment",
        "Group sibling elements without adding an extra native wrapper view.",
    ),
    "memo": (
        "memo",
        "Skip pure component re-renders when props have not changed.",
    ),
    "picker": (
        "Native Picker",
        "Use a real iOS picker trigger and Android Spinner from the same Python element.",
    ),
}

PICKER_ITEMS: list[dict[str, Any]] = [{"value": value, "label": title} for value, (title, _) in FEATURES.items()]


def release_heading() -> pn.Element:
    return pn.Fragment(
        pn.Text(
            "PythonNative v0.16.0",
            style=pn.style(font_size=28, font_weight="700"),
        ),
        pn.Text(
            "Cleaner component APIs, better composition, and more native controls.",
            style=pn.style(color="#4B5563", line_height=22),
        ),
    )


@pn.memo
@pn.component
def FeatureCard(title: str, body: str) -> pn.Element:
    return pn.View(
        pn.Text(title, style=pn.style(font_size=18, font_weight="700")),
        pn.Text(body, style=pn.style(color="#374151", line_height=21)),
        style=pn.style(
            padding=16,
            spacing=8,
            border_radius=16,
            border_width=1,
            border_color="#E5E7EB",
            background_color="#FFFFFF",
        ),
    )


@pn.component
def App() -> pn.Element:
    selected, set_selected = pn.use_state("props")
    opacity = pn.use_animated_value(0.0)
    scale = pn.use_animated_value(0.96)

    def enter() -> None:
        pn.Animated.parallel(
            [
                pn.Animated.timing(opacity, to=1.0, duration=300),
                pn.Animated.spring(scale, to=1.0, stiffness=220, damping=18),
            ]
        ).start()

    pn.use_effect(enter, [])

    title, body = FEATURES.get(str(selected), FEATURES["props"])

    return pn.SafeAreaView(
        pn.Animated.View(
            release_heading(),
            pn.Picker(
                value=selected,
                items=PICKER_ITEMS,
                on_change=set_selected,
                accessibility_label="Choose a v0.16.0 feature",
                style=pn.style(padding=12, border_radius=12, border_width=1, border_color="#D1D5DB"),
            ),
            FeatureCard(title, body),
            style=pn.style(opacity=opacity, scale=scale, padding=24, spacing=18, background_color="#F9FAFB"),
        )
    )
