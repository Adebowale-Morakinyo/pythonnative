from typing import Any

import pythonnative as pn


class MainPage(pn.Page):
    def __init__(self, native_instance: Any) -> None:
        super().__init__(native_instance)
        self.state = {"count": 0}

    def increment(self) -> None:
        self.set_state(count=self.state["count"] + 1)

    def render(self) -> pn.Element:
        return pn.ScrollView(
            pn.Column(
                pn.Text("Hello from PythonNative Demo!", font_size=24, bold=True),
                pn.Text(f"Tapped {self.state['count']} times", font_size=16),
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
