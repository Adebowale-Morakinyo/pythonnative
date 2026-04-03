import emoji

import pythonnative as pn

MEDALS = [":1st_place_medal:", ":2nd_place_medal:", ":3rd_place_medal:"]


styles = pn.StyleSheet.create(
    title={"font_size": 24, "bold": True},
    subtitle={"font_size": 16, "color": "#666666"},
    medal={"font_size": 32},
    section={"spacing": 12, "padding": 16, "align_items": "stretch"},
)


@pn.component
def counter_badge(initial: int = 0) -> pn.Element:
    """Reusable counter component with its own hook-based state."""
    count, set_count = pn.use_state(initial)
    medal = emoji.emojize(MEDALS[count] if count < len(MEDALS) else ":star:")

    return pn.Column(
        pn.Text(f"Tapped {count} times", style=styles["subtitle"]),
        pn.Text(medal, style=styles["medal"]),
        pn.Button("Tap me", on_click=lambda: set_count(count + 1)),
        style={"spacing": 4},
    )


@pn.component
def MainPage() -> pn.Element:
    nav = pn.use_navigation()
    return pn.ScrollView(
        pn.Column(
            pn.Text("Hello from PythonNative Demo!", style=styles["title"]),
            counter_badge(),
            pn.Button(
                "Go to Second Page",
                on_click=lambda: nav.push(
                    "app.second_page.SecondPage",
                    args={"message": "Greetings from MainPage"},
                ),
            ),
            style=styles["section"],
        )
    )
