from typing import Any

import emoji

import pythonnative as pn

MEDALS = [":1st_place_medal:", ":2nd_place_medal:", ":3rd_place_medal:"]


class MainPage(pn.Page):
    def __init__(self, native_instance: Any) -> None:
        super().__init__(native_instance)
        self.state = {"count": 0}

    def increment(self) -> None:
        self.set_state(count=self.state["count"] + 1)

    def render(self) -> pn.Element:
        count = self.state["count"]
        medal = emoji.emojize(MEDALS[count] if count < len(MEDALS) else ":star:")
        return pn.ScrollView(
            pn.Column(
                pn.Text("Hello from PythonNative Demo!", font_size=24, bold=True),
                pn.Text(f"Tapped {count} times", font_size=16),
                pn.Text(medal, font_size=32),
                pn.Button("Tap me", on_click=self.increment, background_color="#FF1E88E5"),
                pn.Button(
                    "Go to Second Page",
                    on_click=lambda: self.push(
                        "app.second_page.SecondPage",
                        args={"message": "Greetings from MainPage"},
                    ),
                ),
                spacing=12,
                padding=16,
                alignment="fill",
            )
        )
