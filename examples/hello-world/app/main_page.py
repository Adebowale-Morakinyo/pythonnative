from typing import Callable

import emoji

import pythonnative as pn
from pythonnative.navigation import NavigationContainer, create_tab_navigator

print("[hello-world] main_page module imported")

MEDALS = [":1st_place_medal:", ":2nd_place_medal:", ":3rd_place_medal:"]

Tab = create_tab_navigator()

styles = pn.StyleSheet.create(
    title={"font_size": 24, "bold": True},
    subtitle={"font_size": 16, "color": "#666666"},
    medal={"font_size": 32},
    card={
        "spacing": 12,
        "padding": 16,
        "background_color": "#F8F9FA",
        "align_items": "center",
    },
    section={"spacing": 16, "padding": 24, "align_items": "stretch"},
    button_row={"spacing": 8, "align_items": "center"},
)


@pn.component
def counter_badge(initial: int = 0) -> pn.Element:
    """Reusable counter component with its own hook-based state."""
    count, set_count = pn.use_state(initial)
    medal = emoji.emojize(MEDALS[count] if count < len(MEDALS) else ":star:")

    print(f"[counter_badge] render count={count}")

    def handle_tap() -> None:
        print(f"[counter_badge] Tap me clicked; {count} -> {count + 1}")
        set_count(count + 1)

    def handle_reset() -> None:
        print(f"[counter_badge] Reset clicked from count={count}")
        set_count(0)

    return pn.View(
        pn.Text(f"Tapped {count} times", style=styles["subtitle"]),
        pn.Text(medal, style=styles["medal"]),
        pn.Row(
            pn.Button("Tap me", on_click=handle_tap),
            pn.Button("Reset", on_click=handle_reset),
            style=styles["button_row"],
        ),
        style=styles["card"],
    )


@pn.component
def HomeTab() -> pn.Element:
    """Home tab — counter demo and push-navigation to other pages."""
    nav = pn.use_navigation()

    def _on_mount() -> Callable[[], None]:
        print("[HomeTab] mounted")
        return lambda: print("[HomeTab] unmounted")

    pn.use_effect(_on_mount, [])

    def go_to_second() -> None:
        print("[HomeTab] navigating to SecondPage")
        nav.navigate(
            "app.second_page.SecondPage",
            params={"message": "Greetings from MainPage"},
        )

    return pn.ScrollView(
        pn.Column(
            pn.Text("Hello from PythonNative Demo!", style=styles["title"]),
            counter_badge(),
            pn.Button("Go to Second Page", on_click=go_to_second),
            style=styles["section"],
        )
    )


@pn.component
def SettingsTab() -> pn.Element:
    """Settings tab — simple placeholder content."""
    return pn.ScrollView(
        pn.Column(
            pn.Text("Settings", style=styles["title"]),
            pn.Text("App version: 0.7.0", style=styles["subtitle"]),
            pn.Text(
                "This tab uses a native UITabBar on iOS " "and BottomNavigationView on Android.",
                style=styles["subtitle"],
            ),
            style=styles["section"],
        )
    )


@pn.component
def MainPage() -> pn.Element:
    return NavigationContainer(
        Tab.Navigator(
            Tab.Screen("Home", component=HomeTab, options={"title": "Home"}),
            Tab.Screen("Settings", component=SettingsTab, options={"title": "Settings"}),
        )
    )
