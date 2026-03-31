from typing import Any

import pythonnative as pn


class ThirdPage(pn.Page):
    def __init__(self, native_instance: Any) -> None:
        super().__init__(native_instance)

    def render(self) -> pn.Element:
        return pn.Column(
            pn.Text("Third Page", font_size=24, bold=True),
            pn.Text("You navigated two levels deep."),
            pn.Button("Back to Second", on_click=self.pop),
            spacing=12,
            padding=16,
            alignment="fill",
        )
