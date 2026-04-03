from typing import Any

import emoji

import pythonnative as pn

MEDALS = [":1st_place_medal:", ":2nd_place_medal:", ":3rd_place_medal:"]


styles = pn.StyleSheet.create(
    title={"font_size": 24, "bold": True},
    subtitle={"font_size": 16, "color": "#666666"},
    medal={"font_size": 32},
    section={"spacing": 12, "padding": 16, "alignment": "fill"},
)


@pn.component
def counter_badge(initial: int = 0) -> pn.Element:
    """Reusable counter component with its own hook-based state."""
    count, set_count = pn.use_state(initial)
    medal = emoji.emojize(MEDALS[count] if count < len(MEDALS) else ":star:")

    return pn.Column(
        pn.Text(f"Tapped {count} times", **styles["subtitle"]),
        pn.Text(medal, **styles["medal"]),
        pn.Button("Tap me", on_click=lambda: set_count(count + 1)),
        spacing=4,
    )


class MainPage(pn.Page):
    def __init__(self, native_instance: Any) -> None:
        super().__init__(native_instance)

    def render(self) -> pn.Element:
        return pn.ScrollView(
            pn.Column(
                pn.Text("Hello from PythonNative Demo!", **styles["title"]),
                counter_badge(),
                pn.Button(
                    "Go to Second Page",
                    on_click=lambda: self.push(
                        "app.second_page.SecondPage",
                        args={"message": "Greetings from MainPage"},
                    ),
                ),
                **styles["section"],
            )
        )
