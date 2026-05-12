"""Persisted theme: one hook, native storage, no boilerplate.

Tweet options:
1. One hook, native storage, and no boilerplate: your theme survives an app restart. #PythonNative
2. Close the app, reopen it, and your theme is right where you left it. #PythonNative
3. Persist UI state to native storage with a single hook and zero boilerplate. #Python
"""

import pythonnative as pn

PALETTE = {
    "light": {"bg": "#F8FAFC", "card": "#FFFFFF", "fg": "#0F172A"},
    "dark": {"bg": "#020617", "card": "#111827", "fg": "#F8FAFC"},
}


@pn.component
def App() -> pn.Element:
    mode, set_mode = pn.use_persisted_state("demo.theme", "dark")
    colors = PALETTE[mode]
    next_mode = "light" if mode == "dark" else "dark"

    return pn.Column(
        pn.Text(
            f"{mode.title()} mode",
            style=pn.style(
                font_size=34, font_weight="700", color=colors["fg"]
            ),
        ),
        pn.Text(
            "Close the app. Reopen it. The setting is still there.",
            style=pn.style(font_size=16, color=colors["fg"], opacity=0.72),
        ),
        pn.Button(
            f"Switch to {next_mode}", on_click=lambda: set_mode(next_mode)
        ),
        style=pn.style(
            flex=1,
            spacing=16,
            padding=24,
            justify_content="center",
            background_color=colors["bg"],
        ),
    )
