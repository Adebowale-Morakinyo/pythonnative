"""Keyboard-aware form: the focused field stays visible.

Tweet options:
1. A keyboard-aware sign-in form where the focused field always stays visible, built in Python. #PythonNative
2. KeyboardAvoidingView keeps your active input above the keyboard—no layout hacks required. #PythonNative
3. Native keyboard handling, two text fields, and zero fuss, all from Python. #MobileDev
"""

import pythonnative as pn

FIELD = pn.style(
    padding=12,
    border_width=1,
    border_radius=10,
    border_color="#CBD5E1",
    font_size=16,
)


@pn.component
def App() -> pn.Element:
    email, set_email = pn.use_state("")
    password, set_password = pn.use_state("")

    return pn.KeyboardAvoidingView(
        pn.Column(
            pn.Text(
                "Sign in", style=pn.style(font_size=36, font_weight="700")
            ),
            pn.TextInput(
                value=email,
                placeholder="you@example.com",
                keyboard_type="email_address",
                auto_capitalize="none",
                on_change=set_email,
                style=FIELD,
            ),
            pn.TextInput(
                value=password,
                placeholder="Password",
                secure=True,
                on_change=set_password,
                style=FIELD,
            ),
            pn.Button("Continue", on_click=lambda: print(email)),
            style=pn.style(spacing=14, padding=24),
        ),
        behavior="padding",
        style=pn.style(flex=1, justify_content="center"),
    )
