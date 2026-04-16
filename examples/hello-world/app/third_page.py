import pythonnative as pn

print("[hello-world] third_page module imported")


@pn.component
def ThirdPage() -> pn.Element:
    nav = pn.use_navigation()
    print("[ThirdPage] render")

    def go_back() -> None:
        print("[ThirdPage] going back")
        nav.go_back()

    return pn.ScrollView(
        pn.Column(
            pn.Text("Third Page", style={"font_size": 24, "bold": True}),
            pn.Text("You navigated two levels deep."),
            pn.Button("Back to Second", on_click=go_back),
            style={"spacing": 16, "padding": 24, "align_items": "stretch"},
        )
    )
