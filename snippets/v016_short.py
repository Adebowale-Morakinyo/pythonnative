"""v0.16.0 (short): typed components, Fragment, memo, and native Picker.

Tweet options:
1. PythonNative v0.16.0: typed components, Fragment, memo, and a native Picker. #PythonNative
2. Version 0.16.0 ships typed props, Fragment, memo, and a real native Picker. #Python
3. Four upgrades in v0.16.0: typed components, Fragment, memo, and the native Picker. #PythonNative
"""

import pythonnative as pn

FEATURES = {
    "Fragment": "Group siblings without wrapper views.",
    "memo": "Skip pure re-renders.",
    "Picker": "Use real native controls.",
}
ITEMS = [
    {"value": "Fragment", "label": "Fragment"},
    {"value": "memo", "label": "memo"},
    {"value": "Picker", "label": "Picker"},
]


@pn.memo
@pn.component
def FeatureCard(name: str) -> pn.Element:
    return pn.View(
        pn.Text(name, style=pn.style(font_size=20, font_weight="700")),
        pn.Text(FEATURES[name], style=pn.style(color="#4B5563")),
        style=pn.style(
            padding=16,
            spacing=8,
            border_radius=16,
            background_color="#FFFFFF",
        ),
    )


@pn.component
def App() -> pn.Element:
    selected, set_selected = pn.use_state("Fragment")

    return pn.SafeAreaView(
        pn.Column(
            pn.Fragment(
                pn.Text(
                    "PythonNative v0.16.0",
                    style=pn.style(font_size=28, font_weight="700"),
                ),
                pn.Text("Typed props, Fragment, memo, native Picker."),
            ),
            pn.Picker(
                value=selected,
                items=ITEMS,
                on_change=set_selected,
            ),
            FeatureCard(str(selected)),
            style=pn.style(
                padding=24,
                spacing=16,
                background_color="#F9FAFB",
            ),
        )
    )
