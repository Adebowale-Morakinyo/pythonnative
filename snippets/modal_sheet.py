"""Modal sheet: native presentation controlled by one boolean.

Tweet options:
1. A real native modal sheet, presented and dismissed by a single boolean in Python. #PythonNative
2. This isn’t a web overlay—it’s a genuine platform modal, mounted from Python. #iOS
3. Flip one boolean to present a native sheet; flip it back to dismiss. #PythonNative
"""

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    open_, set_open = pn.use_state(False)

    return pn.Column(
        pn.Text(
            "Native modal", style=pn.style(font_size=34, font_weight="700")
        ),
        pn.Button("Open sheet", on_click=lambda: set_open(True)),
        pn.Modal(
            pn.Column(
                pn.Text(
                    "This is not a web overlay.",
                    style=pn.style(font_size=26, font_weight="700"),
                ),
                pn.Text(
                    "It is a real platform modal, mounted from Python.",
                    style=pn.style(font_size=16, color="#475569"),
                ),
                pn.Button("Done", on_click=lambda: set_open(False)),
                style=pn.style(spacing=16, padding=24),
            ),
            visible=open_,
            on_dismiss=lambda: set_open(False),
            title="Details",
            animation_type="slide",
        ),
        style=pn.style(
            flex=1,
            spacing=18,
            padding=24,
            justify_content="center",
            align_items="center",
        ),
    )
