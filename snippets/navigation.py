"""Navigation: a real native stack with two screens.

Tweet options:
1. A real native navigation stack with two screens, defined entirely in Python. #PythonNative
2. Push to a details screen and pop back with a genuine native stack—no web views. #iOS
3. Two screens, one native stack navigator, written in pure Python. #PythonNative
"""

import pythonnative as pn

Stack = pn.create_stack_navigator()


@pn.component
def Home() -> pn.Element:
    nav = pn.use_navigation()
    return pn.Column(
        pn.Text("Home", style=pn.style(font_size=32, font_weight="700")),
        pn.Button("Go to details", on_click=lambda: nav.navigate("Details")),
        style=pn.style(spacing=16, padding=24),
    )


@pn.component
def Details() -> pn.Element:
    nav = pn.use_navigation()
    return pn.Column(
        pn.Text("Details", style=pn.style(font_size=32, font_weight="700")),
        pn.Button("Back", on_click=nav.go_back),
        style=pn.style(spacing=16, padding=24),
    )


@pn.component
def App() -> pn.Element:
    return pn.NavigationContainer(
        Stack.Navigator(
            Stack.Screen("Home", component=Home, options={"title": "Home"}),
            Stack.Screen("Details", component=Details, options={"title": "Details"}),
        )
    )
