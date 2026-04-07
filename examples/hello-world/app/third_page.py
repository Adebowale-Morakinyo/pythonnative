import pythonnative as pn


@pn.component
def ThirdPage() -> pn.Element:
    nav = pn.use_navigation()
    return pn.ScrollView(
        pn.Column(
            pn.Text("Third Page", style={"font_size": 24, "bold": True}),
            pn.Text("You navigated two levels deep."),
            pn.Button("Back to Second", on_click=nav.go_back),
            style={"spacing": 16, "padding": 24, "align_items": "stretch"},
        )
    )
