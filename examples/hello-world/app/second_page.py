from typing import Any

import pythonnative as pn


class SecondPage(pn.Page):
    def __init__(self, native_instance: Any) -> None:
        super().__init__(native_instance)

    def render(self) -> pn.Element:
        message = self.get_args().get("message", "Second Page")
        return pn.ScrollView(
            pn.Column(
                pn.Text(message, font_size=20),
                pn.Button(
                    "Go to Third Page",
                    on_click=lambda: self.push("app.third_page.ThirdPage"),
                ),
                pn.Button("Back", on_click=self.pop),
                spacing=12,
                padding=16,
                alignment="fill",
            )
        )
