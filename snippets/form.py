"""Form: two-way binding between TextInput and a headline.

Tweet options:
1. Two-way binding in PythonNative is just use_state: type in the field, and the headline updates live. #PythonNative
2. Type a name, and the greeting updates instantly—two-way binding in pure Python. #PythonNative
3. A native TextInput wired to a live headline, in a handful of lines of Python. #Python
"""

import pythonnative as pn


@pn.component
def App() -> pn.Element:
    name, set_name = pn.use_state("")
    return pn.Column(
        pn.Text(
            f"Hi, {name or 'stranger'}!",
            style=pn.style(font_size=32, font_weight="700"),
        ),
        pn.TextInput(
            value=name,
            placeholder="Your name",
            on_change=set_name,
            style=pn.style(
                padding=12,
                border_width=1,
                border_radius=8,
                border_color="#D1D5DB",
                font_size=16,
            ),
        ),
        style=pn.style(spacing=16, padding=24),
    )
