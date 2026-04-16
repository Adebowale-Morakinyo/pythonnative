import pythonnative as pn

print("[hello-world] second_page module imported")


@pn.component
def SecondPage() -> pn.Element:
    nav = pn.use_navigation()
    message = nav.get_params().get("message", "Second Page")
    print(f"[SecondPage] render message={message!r}")

    def go_to_third() -> None:
        print("[SecondPage] navigating to ThirdPage")
        nav.navigate("app.third_page.ThirdPage")

    def go_back() -> None:
        print("[SecondPage] going back")
        nav.go_back()

    return pn.ScrollView(
        pn.Column(
            pn.Text(message, style={"font_size": 24, "bold": True}),
            pn.Button("Go to Third Page", on_click=go_to_third),
            pn.Button("Back", on_click=go_back),
            style={"spacing": 16, "padding": 24, "align_items": "stretch"},
        )
    )
