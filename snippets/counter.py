"""Counter: the canonical "first app".

Tweet options:
1. The canonical first app in PythonNative: a tap counter in a handful of lines. #PythonNative
2. Tap to increment a counter with use_state—the simplest PythonNative demo. #PythonNative
3. A native button and a single state value—your first PythonNative counter. #Python
"""

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    count, set_count = pn.use_state(0)
    return pn.Column(
        pn.Text(f"Count: {count}", style=pn.style(font_size=32, font_weight="700")),
        pn.Button("Tap me", on_click=lambda: set_count(count + 1)),
        style=pn.style(spacing=16, padding=24, align_items="center"),
    )
