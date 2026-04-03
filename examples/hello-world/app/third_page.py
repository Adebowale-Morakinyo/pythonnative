import pythonnative as pn


@pn.component
def ThirdPage() -> pn.Element:
    nav = pn.use_navigation()
    return pn.Column(
        pn.Text("Third Page", style={"font_size": 24, "bold": True}),
        pn.Text("You navigated two levels deep."),
        pn.Button("Back to Second", on_click=nav.pop),
        style={"spacing": 12, "padding": 16, "align_items": "stretch"},
    )
