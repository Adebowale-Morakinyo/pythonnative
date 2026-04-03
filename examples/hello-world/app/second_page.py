import pythonnative as pn


@pn.component
def SecondPage() -> pn.Element:
    nav = pn.use_navigation()
    message = nav.get_args().get("message", "Second Page")
    return pn.ScrollView(
        pn.Column(
            pn.Text(message, style={"font_size": 20}),
            pn.Button(
                "Go to Third Page",
                on_click=lambda: nav.push("app.third_page.ThirdPage"),
            ),
            pn.Button("Back", on_click=nav.pop),
            style={"spacing": 12, "padding": 16, "align_items": "stretch"},
        )
    )
