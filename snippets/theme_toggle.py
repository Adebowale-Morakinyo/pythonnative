"""Theme toggle: flip the whole tree from light to dark.

Tweet options:
1. Flip your entire view tree from light to dark with a single piece of state. #PythonNative
2. Light or dark, the whole UI updates from one Python state value. #PythonNative
3. A native light and dark theme toggle, driven by plain Python state. #MobileDev
"""

import pythonnative as pn

THEMES = {
    "light": {"bg": "#FFFFFF", "fg": "#0F172A"},
    "dark": {"bg": "#0F172A", "fg": "#F8FAFC"},
}


@pn.component
def App() -> pn.Element:
    mode, set_mode = pn.use_state("light")
    t = THEMES[mode]
    next_mode = "dark" if mode == "light" else "light"

    return pn.Column(
        pn.Text("Hello, native.", style=pn.style(font_size=32, color=t["fg"])),
        pn.Button(f"Switch to {next_mode}", on_click=lambda: set_mode(next_mode)),
        style=pn.style(
            flex=1,
            spacing=16,
            padding=24,
            justify_content="center",
            background_color=t["bg"],
        ),
    )
